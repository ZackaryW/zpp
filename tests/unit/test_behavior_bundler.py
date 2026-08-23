import subprocess
from pathlib import Path
from uuid import uuid4

from openspec_bundler import InMemoryStoreProvider, RegisteredStore

from zpp.core.behavior import BehaviorRunInput
from zpp.utils.behavior import BundlerBehaviorDocuments
from zpp.utils.processes import ProcessResult


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

    def run(self, arguments, *, cwd):
        self.calls.append((tuple(arguments), cwd))
        return ProcessResult(tuple(arguments), 0, "verified\n", "")


def _provider(repository: Path) -> InMemoryStoreProvider:
    identity = uuid4()
    repository.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    openspec = repository / "openspec"
    openspec.mkdir(parents=True)
    (openspec / "bundler.toml").write_text(
        f'version = 1\nuuid = "{identity}"\n', encoding="utf-8"
    )
    return InMemoryStoreProvider((RegisteredStore("test", repository),))


def test_behavior_document_initializes_dedicated_yaml_without_lease_state(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    provider = _provider(repository)

    report = BundlerBehaviorDocuments(provider).initialize(repository)

    path = repository / "zpp.behave.yaml"
    assert path.read_text(encoding="utf-8") == "version: 1\ncommands: {}\n"
    assert report.root == repository.resolve()
    assert report.commands == ()


def test_behavior_document_runs_one_complete_command_directly(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    provider = _provider(repository)
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
""",
        encoding="utf-8",
    )
    runner = FakeRunner()
    documents = BundlerBehaviorDocuments(
        provider, adapters=(FakeAdapter(),), runner=runner
    )

    report = documents.run(repository, BehaviorRunInput("bdd", complete=True))

    assert tuple(target.name for target in report.targets) == ("core",)
    assert report.result is not None
    assert report.result.stdout == "verified\n"
    assert runner.calls == [(("verify", "features/core"), repository.resolve())]
