from pathlib import Path

from openlease import (
    CallbackEvent,
    CallbackMode,
    ConfigurationLayout,
    ConfigurationTarget,
    ExtensionContext,
    ExtensionEvent,
    ExtensionInvocation,
    ExtensionMember,
)
from openlease.utils.processes import ProcessResult

from zpp.core.behavior import BehaviorRunInput
from zpp.utils.openlease import (
    OpenLeaseBehaviorDocuments,
    behavior_extension,
    create_zpp_openlease,
)


class FakeAdapter:
    kind = "fake"

    def validate(self, raw):
        assert raw == {"kind": "fake", "prefix": "verify"}
        return "verify"

    def argv(self, root, settings, targets):
        return (str(settings), *targets)


class FakeRunner:
    def __init__(self) -> None:
        self.calls = []

    def run(self, arguments, *, cwd=None, env=None):
        del env
        self.calls.append((tuple(arguments), cwd))
        return ProcessResult(tuple(arguments), 0, "verified\n", "")


def test_behavior_extension_registers_exact_operations_and_callbacks(
    tmp_path: Path,
) -> None:
    registration = behavior_extension(state_root=tmp_path / "state")

    assert registration.manifest.identifier == "zpp.behave"
    assert [(item.name, item.target_kinds) for item in registration.operations] == [
        ("initialize", ("direct",)),
        ("run", ("direct", "repository", "cohort")),
    ]
    assert [
        (item.event, item.operation, item.modes) for item in registration.callbacks
    ] == [
        (
            CallbackEvent.RECONCILE_BEFORE_REPOSITORY,
            "run",
            (CallbackMode.GATE, CallbackMode.OBSERVE),
        ),
        (
            CallbackEvent.RECONCILE_AFTER_REPOSITORY,
            "run",
            (CallbackMode.OBSERVE,),
        ),
        (
            CallbackEvent.RECONCILE_AFTER_COHORT,
            "run",
            (CallbackMode.OBSERVE,),
        ),
    ]


def test_behavior_document_initializes_dedicated_yaml_without_a_space(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    lifecycle = create_zpp_openlease(tmp_path / "state")

    report = OpenLeaseBehaviorDocuments(lifecycle).initialize(repository)

    path = repository / "zpp.behave.yaml"
    assert path.is_file()
    assert "version: 1" in path.read_text()
    assert "zpp.behave:" not in path.read_text()
    assert report.root == repository.resolve()
    assert report.commands == ()
    assert lifecycle.snapshot().spaces == ()


def test_behavior_document_runs_one_complete_command_directly(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "zpp.behave.yaml").write_text(
        """version: 1
commands:
  bdd:
    provider:
      kind: fake
      prefix: verify
    targets:
      core:
        value: features/core
        paths: [src/core/**]
"""
    )
    runner = FakeRunner()
    lifecycle = create_zpp_openlease(
        tmp_path / "state",
        behavior_adapters=(FakeAdapter(),),
        behavior_runner=runner,
    )

    report = OpenLeaseBehaviorDocuments(lifecycle).run(
        repository, BehaviorRunInput("bdd", complete=True)
    )

    assert tuple(target.name for target in report.targets) == ("core",)
    assert report.result is not None
    assert report.result.stdout == "verified\n"
    assert runner.calls == [(("verify", "features/core"), repository.resolve())]


def test_callback_reopens_the_exact_repository_behavior_document(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    mapping = repository / "zpp.behave.yaml"
    mapping.write_text(
        """version: 1
commands:
  bdd:
    provider: {kind: fake, prefix: verify}
    targets:
      core: {value: features/core, paths: [src/core/**]}
"""
    )
    state_root = tmp_path / "state"
    runner = FakeRunner()
    lifecycle = create_zpp_openlease(
        state_root,
        behavior_adapters=(FakeAdapter(),),
        behavior_runner=runner,
    )
    direct = lifecycle.bind_extension_document(
        "zpp.behave",
        mapping,
        codec="yaml",
        layout=ConfigurationLayout.DEDICATED,
        repository_path=repository,
    )
    registration = behavior_extension(
        (FakeAdapter(),), runner=runner, state_root=state_root
    )
    operation = next(item for item in registration.operations if item.name == "run")
    context = ExtensionContext(
        extension_id="zpp.behave",
        target_kind="cohort",
        target=ConfigurationTarget.repository("repo"),
        state_generation=1,
        configuration_generation=1,
        roots=direct.context.roots,
        space_id="work",
        members=(
            ExtensionMember(
                "repo", repository, repository, "abc", "work", False, "write"
            ),
        ),
    )
    invocation = ExtensionInvocation(
        {"command": "bdd", "complete": True},
        context,
        direct.config,
        direct.data,
        direct.cache,
        ExtensionEvent(
            CallbackEvent.RECONCILE_AFTER_COHORT,
            CallbackMode.OBSERVE,
            repository_id="repo",
            cohort_id="work",
        ),
    )

    report = operation.handler(invocation)

    assert tuple(target.name for target in report.targets) == ("core",)
    assert runner.calls == [(("verify", "features/core"), repository.resolve())]
