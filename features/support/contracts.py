from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType
from unittest.mock import patch

from agent_router import Agent
from typer.testing import CliRunner

from zpp.artifacts import (
    PACKAGED_AUTHORING_SKILL_NAMES,
    packaged_trait_source,
    packaged_traits,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
from zpp.cli import app
from zpp.cli.reset import reset_projections
from zpp.cli.shared import agent_router
from zpp.core.application import TraitApplication, TraitInvocation
from zpp.core.catalog import decode_trait_document
from zpp.core.composition import compose_trait_family
from zpp.core.evidence import EvidenceRuntime
from zpp.core.models import ActivationMode, SourceKind, SourceRef
from zpp.utils.agent_selection import (
    AgentSelection,
    AgentSelectionError,
    normalize_agent_selection,
    select_many_agents,
    select_one_agent,
)
from zpp.utils.openlease import (
    behavior_extension,
    create_trait_documents,
    create_zpp_openlease,
)
from zpp.utils.openspec import OPENSPEC_CORE_SKILL_NAMES


def verify_workflow_contract() -> None:
    skill = packaged_workflow_skill()
    text = next(
        item.content.decode("utf-8")
        for item in skill.files
        if item.relative_path == "SKILL.md"
    )
    families = {item.family for item in packaged_traits()}
    assert skill.name == "zpp-workflow"
    assert skill.compatible_agents == frozenset(Agent)
    assert "workflow" not in families
    assert "automatic-workflow" not in families
    assert "workflow-authority" not in families
    for phrase in (
        "Require an explicit current stage",
        "Traits advise the selected stage",
        "Automatic progression",
        "distinct, visible action",
        "OpenLease only through its public",
        "Agent Router only through its public",
        "Ignore retained ZPP 1.x stage skills",
        "already injected by the agent-native ZPP hook",
        "stage-neutral",
        "Reconcile the complete agreement",
        "A recommendation is not confirmation",
        "Unresolved — Do Not Assume",
        "supersede downstream checkpoints",
        "skipped: not applicable",
        "Clarification has not converged",
    ):
        assert phrase in text
    assert "zpp resolve" not in text
    assert "ZPP_CONTEXT" not in text
    assert {
        "bdd",
        "bdd-execution",
        "bdd-structure",
        "build",
        "dependencies",
        "tdd",
        "tooling",
        "zero-assumptions",
    } == families

    documents = {
        item.family: tomllib.loads(item.content.decode("utf-8"))
        for item in packaged_traits()
    }
    assert documents["zero-assumptions"]["meta"]["activation"] == "always-run"
    assert [
        flavor.get("facet", {}).get("bdd_mode")
        for flavor in documents["bdd-execution"]["trait"]
    ] == ["manual", "disabled", "complete", "targeted", None]
    execution_bodies = [
        flavor["content"]["body"] for flavor in documents["bdd-execution"]["trait"]
    ]
    assert "absence of `zpp.behave.yaml` never blocks native BDD" in text
    assert "complete established native BDD suite" in text
    assert "optional `zpp behave` coordination" in execution_bodies[2]
    assert "established native BDD feature surface directly" in execution_bodies[3]
    assert "established native feature surface directly" in execution_bodies[4]
    assert "zpp-flow-wire-feature" not in text
    assert all("zpp-flow-" not in body for body in execution_bodies)
    assert [flavor["facet"]["tool"] for flavor in documents["tooling"]["trait"]] == [
        "rg",
        "jq",
    ]


def verify_repository_contract() -> None:
    runner = CliRunner()
    root = runner.invoke(app, ["--help"])
    workflow = runner.invoke(app, ["workflow", "--help"])
    trait = runner.invoke(app, ["trait", "--help"])
    assert root.exit_code == workflow.exit_code == trait.exit_code == 0
    assert all(
        name in root.stdout
        for name in (
            "init",
            "open",
            "reset",
            "resolve",
            "behave",
            "trait",
            "workflow",
        )
    )
    assert all(name in workflow.stdout for name in ("install", "update", "remove"))
    assert "space" not in root.stdout
    assert "install-workflow" not in root.stdout

    selected = normalize_agent_selection((Agent.CODEX, Agent.PI, Agent.CODEX))
    assert selected.agents == (Agent.CODEX, Agent.PI)
    cancelled = select_many_agents(
        (),
        required=True,
        interactive=True,
        prompt=lambda: AgentSelection((), cancelled=True),
    )
    assert cancelled.cancelled
    try:
        select_many_agents(
            (),
            required=True,
            interactive=False,
            prompt=lambda: AgentSelection(()),
        )
    except AgentSelectionError:
        pass
    else:
        raise AssertionError("noninteractive omission was accepted")
    try:
        select_one_agent((Agent.CODEX, Agent.PI), required=False)
    except AgentSelectionError:
        pass
    else:
        raise AssertionError("several invoking agents were accepted")

    with TemporaryDirectory() as directory:
        base = Path(directory)
        repository = base / "repository"
        repository.mkdir()
        documents = create_trait_documents(base / "state")
        documents.initialize_context(repository)
        documents.initialize_trait(
            repository,
            "bdd",
            {
                "meta": {"selection": "first-win"},
                "trait": [{"content": {"body": "repository"}}],
            },
        )
        bound = documents.read_repository(repository)
        assert bound.context is not None
        assert [item.family for item in bound.source.documents] == ["bdd"]
        assert sorted(
            str(path.relative_to(repository))
            for path in repository.rglob("*")
            if path.is_file()
        ) == [".zpp/traits/bdd.toml", ".zpp/zpp.toml"]
        subprocess.run(("git", "init", "--quiet"), cwd=repository, check=True)
        subprocess.run(
            ("git", "config", "user.email", "test@example.invalid"),
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ("git", "config", "user.name", "Test"),
            cwd=repository,
            check=True,
        )
        subprocess.run(("git", "add", "."), cwd=repository, check=True)
        subprocess.run(
            ("git", "commit", "--quiet", "-m", "base"),
            cwd=repository,
            check=True,
        )
        prior = Path.cwd()
        try:
            os.chdir(repository)
            behavior_home = base / "behavior-home"
            initialized = runner.invoke(
                app,
                ["--path", str(behavior_home), "behave", "init"],
            )
        finally:
            os.chdir(prior)
        assert initialized.exit_code == 0, initialized.output
        assert (repository / "zpp.behave.yaml").is_file()
        assert create_zpp_openlease(behavior_home / "openlease").snapshot().spaces == ()
        router = agent_router(Agent.CODEX, repository)
        assert router.environment.root == Path.home().resolve()
        assert router.environment.project_root == repository.resolve()


def verify_catalog_contract() -> None:
    source = packaged_trait_source()
    assert source.identifier == "zpp:packaged"
    assert all("trait" in item.values for item in source.documents)
    for item in source.documents:
        decoded = decode_trait_document(
            item.family,
            item.values,
            SourceRef(SourceKind.GLOBAL, item.identifier or item.family),
        )
        assert decoded.flavors
        expected_activation = (
            ActivationMode.ALWAYS_RUN
            if item.family == "zero-assumptions"
            else ActivationMode.AUTOMATIC
        )
        assert decoded.activation is expected_activation
        assert all(flavor.content.body for flavor in decoded.flavors)

    def document(
        kind: SourceKind,
        body: str,
        mode: str | None = None,
        activation: str | None = None,
    ):
        meta = {"selection": "extend"}
        if mode is not None:
            meta["mode"] = mode
        if activation is not None:
            meta["activation"] = activation
        return decode_trait_document(
            "bdd",
            {"meta": meta, "trait": [{"content": {"body": body}}]},
            SourceRef(kind, body),
        )

    layered = compose_trait_family(
        "bdd",
        [
            document(SourceKind.GLOBAL, "global", activation="always-run"),
            document(SourceKind.SPACE, "space"),
            document(
                SourceKind.REPOSITORY,
                "repository",
                activation="manual",
            ),
        ],
    )
    assert [item.flavor.content.body for item in layered.flavors] == [
        "repository",
        "space",
        "global",
    ]
    assert layered.activation is ActivationMode.MANUAL
    overwritten = compose_trait_family(
        "bdd",
        [
            document(SourceKind.GLOBAL, "global"),
            document(
                SourceKind.REPOSITORY,
                "repository",
                "repository-overwrite",
            ),
        ],
    )
    assert [item.flavor.content.body for item in overwritten.flavors] == ["repository"]


def verify_resolution_contract() -> None:
    with TemporaryDirectory() as directory:
        target = Path(directory)
        (target / "pyproject.toml").write_text(
            "[project]\nname='example'\ndependencies=['click']\n"
        )
        application = TraitApplication(
            lambda root: EvidenceRuntime(root, Path.read_bytes, shutil.which)
        )
        result = application.resolve(
            TraitInvocation(
                target=target,
                stage="wire",
                facets=MappingProxyType(
                    {
                        "language": ("python", "flutter"),
                        "build_tool": "uv",
                    }
                ),
                stored_context=None,
                repository_context=None,
                sources=(packaged_trait_source(),),
            )
        )
        families = [body.family for body in result.bodies]
        assert "bdd" in families
        assert "tdd" in families
        assert "dependencies" in families
        assert result.resolution.context.values["stage"] == "wire"
        assert "stage" not in json.loads(result.context)["facets"]
        assert result.explanation["context"]["members"]
        assert result.explanation["families"]
        assert result.context

        traits = target / ".zpp" / "traits"
        traits.mkdir(parents=True)
        (traits / "manual-policy.toml").write_text(
            "[meta]\nselection='all'\nactivation='manual'\n"
            "[[trait]]\n[trait.facet]\nlanguage='python'\n"
            "[trait.content]\nbody='manual policy'\n"
        )
        direct = CliRunner().invoke(
            app,
            [
                "resolve",
                str(target),
                "--trait",
                "manual-policy",
                "--facet",
                "language=python",
            ],
        )
        common = CliRunner().invoke(
            app,
            ["resolve", str(target), "--facet", "language=python"],
        )
        assert direct.exit_code == common.exit_code == 0
        assert direct.stdout == "manual policy"
        assert "manual policy" not in common.stdout


def verify_automatic_hook_contract() -> None:
    native_formats = {
        Agent.CODEX: "json",
        Agent.CLAUDE: "json",
        Agent.KIMI: "toml",
        Agent.PI: "pi-file",
    }
    for agent in Agent:
        hook = packaged_workflow_hook(agent)
        payload = repr(hook.fragment) + "".join(
            item.content.decode("utf-8") for item in hook.files
        )
        assert hook.compatible_agents == frozenset({agent})
        assert hook.format == native_formats[agent]
        assert f"--agent {agent.value} ." in payload or (
            f'"--agent", "{agent.value}"' in payload
        )
        assert "guard" not in payload
        assert "UserPromptSubmit" not in payload

    with TemporaryDirectory() as directory:
        project = Path(directory)
        runner = CliRunner()
        installed = runner.invoke(
            app,
            [
                "workflow",
                "install",
                "--agent",
                "codex",
                "--target",
                str(project),
            ],
        )
        assert installed.exit_code == 0, installed.output
        assert len(json.loads(installed.stdout)) == 2
        removed = runner.invoke(
            app,
            [
                "workflow",
                "remove",
                "--agent",
                "codex",
                "--target",
                str(project),
            ],
        )
        assert removed.exit_code == 0, removed.output
        assert len(json.loads(removed.stdout)) == 2


def verify_product_home_contract() -> None:
    runner = CliRunner()
    catalog = reset_projections()
    assert [(item.agent, item.kind) for item in catalog] == [
        item
        for agent in ("codex", "claude", "pi", "kimi")
        for item in (
            (agent, "hook"),
            (agent, "skill"),
            *(
                (agent, f"skill:{name}")
                for name in PACKAGED_AUTHORING_SKILL_NAMES
            ),
            *(
                (agent, f"skill:{name}")
                for name in OPENSPEC_CORE_SKILL_NAMES
            ),
        )
    ]

    with TemporaryDirectory() as directory:
        root = Path(directory)
        home = root / "selected-home"
        with patch("zpp.cli.open.open_directory") as opener:
            opened = runner.invoke(app, ["--path", str(home), "open"])
        assert opened.exit_code == 0, opened.output
        opener.assert_called_once_with(home)
        assert home.is_dir()
        assert not (home / "openlease").exists()

        unconfirmed = runner.invoke(app, ["--path", str(home), "reset"])
        assert unconfirmed.exit_code == 2
        assert "--yes" in unconfirmed.output

        state = home / "openlease"
        state.mkdir()
        (state / "old.json").write_text("old")
        sibling = home / "notes.txt"
        sibling.write_text("keep")
        with patch("zpp.cli.reset.reset_projections", return_value=()):
            reset = runner.invoke(
                app,
                ["--path", str(home), "reset", "--yes"],
            )
        assert reset.exit_code == 0, reset.output
        assert json.loads(reset.stdout)["state"] == "replaced"
        assert list(state.iterdir()) == []
        assert sibling.read_text() == "keep"


@lru_cache(maxsize=1)
def verify_openspec_skill_provisioning_contract() -> None:
    runner = CliRunner()
    for operation in ("install", "update", "remove"):
        help_result = runner.invoke(app, ["workflow", operation, "--help"])
        assert help_result.exit_code == 0
        assert "openspec" not in help_result.stdout.casefold()

    with TemporaryDirectory() as directory:
        root = Path(directory)
        user_home = root / "user"
        user_home.mkdir()
        with patch.object(
            Path,
            "home",
            classmethod(lambda cls: user_home),
        ):
            initialized = runner.invoke(app, ["init", "--agent", "codex"])
            assert initialized.exit_code == 0, initialized.output
            assert len(json.loads(initialized.stdout)) == 10
            generated = user_home / ".codex/skills/openspec-apply-change"
            provenance = generated / ".zpp-openspec.json"
            assert json.loads(provenance.read_text())["generator"] == "zpp"
            (generated / "SKILL.md").write_text("modified", encoding="utf-8")

            product_home = root / "zpp-home"
            reset = runner.invoke(
                app,
                ["--path", str(product_home), "reset", "--yes"],
            )
            assert reset.exit_code == 0, reset.output
            assert not generated.exists()
            assert (product_home / "openlease").is_dir()


def verify_behavior_contract() -> None:
    runner = CliRunner()
    root_help = runner.invoke(app, ["--help"])
    behavior_help = runner.invoke(app, ["behave", "--help"])
    assert root_help.exit_code == behavior_help.exit_code == 0
    assert "behave" in root_help.stdout
    for option in ("--all", "--target", "--gate", "--base", "--head"):
        assert option in behavior_help.stdout

    registration = behavior_extension()
    assert registration.manifest.identifier == "zpp.behave"
    assert [item.name for item in registration.operations] == ["initialize", "run"]
    assert len(registration.callbacks) == 3

    with TemporaryDirectory() as directory:
        base = Path(directory)
        repository = base / "repository"
        repository.mkdir()

        def git(*arguments: str) -> None:
            subprocess.run(
                ("git", *arguments),
                cwd=repository,
                check=True,
                capture_output=True,
            )

        git("init", "--quiet")
        git("config", "user.email", "test@example.invalid")
        git("config", "user.name", "Test")
        (repository / "tracked.txt").write_text("base\n")
        git("add", ".")
        git("commit", "--quiet", "-m", "base")
        product_home = base / "home"
        prior = Path.cwd()
        try:
            os.chdir(repository)
            initialized = runner.invoke(
                app,
                ["--path", str(product_home), "behave", "init"],
            )
            assert initialized.exit_code == 0, initialized.output
            mapping = repository / "zpp.behave.yaml"
            mapping.write_text(
                "version: 1\n"
                "commands:\n"
                "  bdd:\n"
                "    provider:\n"
                "      kind: argv\n"
                f"      argv: [{json.dumps(sys.executable)}, -c, "
                '"import sys; print(\'|\'.join(sys.argv[1:]))", "{targets}"]\n'
                "    targets:\n"
                "      core: {value: features/core, paths: [src/core/**]}\n"
                "      workflow: {value: features/workflow, paths: [src/workflow/**]}\n"
                "    gates:\n"
                "      zpp-workflow: [workflow, core]\n"
            )
            authored = mapping.read_text()
            validated = runner.invoke(
                app,
                ["--path", str(product_home), "behave", "init"],
            )
            assert validated.exit_code == 0, validated.output
            assert "Behavior mapping validated" in validated.stdout
            assert mapping.read_text() == authored
            git("add", "zpp.behave.yaml")
            git("commit", "--quiet", "-m", "behavior")

            clean = runner.invoke(
                app,
                ["--path", str(product_home), "behave", "bdd"],
            )
            assert clean.exit_code == 0, clean.output
            assert "No targets are affected" in clean.stdout

            changed = repository / "src" / "core" / "module.py"
            changed.parent.mkdir(parents=True)
            changed.write_text("changed\n")
            affected = runner.invoke(
                app,
                ["--path", str(product_home), "behave", "bdd"],
            )
            assert affected.exit_code == 0, affected.output
            assert affected.stdout == "features/core\n"

            complete = runner.invoke(
                app,
                ["--path", str(product_home), "behave", "bdd", "--all"],
            )
            assert complete.exit_code == 0, complete.output
            assert complete.stdout == "features/core|features/workflow\n"

            exact = runner.invoke(
                app,
                [
                    "--path",
                    str(product_home),
                    "behave",
                    "bdd",
                    "--target",
                    "workflow",
                    "--target",
                    "workflow",
                ],
            )
            assert exact.exit_code == 0, exact.output
            assert exact.stdout == "features/workflow\n"

            gate = runner.invoke(
                app,
                [
                    "--path",
                    str(product_home),
                    "behave",
                    "bdd",
                    "--gate",
                    "zpp-workflow",
                ],
            )
            assert gate.exit_code == 0, gate.output
            assert gate.stdout == "features/core|features/workflow\n"

            ambiguous = runner.invoke(
                app,
                ["behave", "bdd", "--all", "--target", "core"],
            )
            assert ambiguous.exit_code == 2
            assert "mutually exclusive" in ambiguous.output
        finally:
            os.chdir(prior)

        assert create_zpp_openlease(product_home / "openlease").snapshot().spaces == ()


VERIFIERS = {
    "behavior_verification": verify_behavior_contract,
    "consolidated_workflow_skill": verify_workflow_contract,
    "repository_trait_bootstrap": verify_repository_contract,
    "toml_trait_catalog": verify_catalog_contract,
    "trait_resolution": verify_resolution_contract,
    "automatic_trait_hooks": verify_automatic_hook_contract,
    "product_home_lifecycle": verify_product_home_contract,
    "openspec_skill_provisioning": verify_openspec_skill_provisioning_contract,
}


def verify_capability(name: str) -> None:
    VERIFIERS[name]()
