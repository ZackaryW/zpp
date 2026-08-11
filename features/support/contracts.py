from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType

from agent_router import Agent
from typer.testing import CliRunner

from zpp.artifacts import (
    packaged_trait_source,
    packaged_traits,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
from zpp.cli import app
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
from zpp.utils.openlease import create_trait_documents


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
    ):
        assert phrase in text
    assert "zpp resolve" not in text
    assert "ZPP_CONTEXT" not in text
    assert {
        "bdd",
        "bdd-structure",
        "bdd-workflow",
        "build",
        "dependencies",
        "tdd",
        "tooling",
        "lease-complete-affected-set",
        "lease-conflict-policy",
        "reconciliation-gate",
        "zero-assumptions",
    } == families


def verify_repository_contract() -> None:
    runner = CliRunner()
    root = runner.invoke(app, ["--help"])
    workflow = runner.invoke(app, ["workflow", "--help"])
    trait = runner.invoke(app, ["trait", "--help"])
    assert root.exit_code == workflow.exit_code == trait.exit_code == 0
    assert all(name in root.stdout for name in ("init", "resolve", "trait", "workflow"))
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
        assert decoded.activation is ActivationMode.AUTOMATIC
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


VERIFIERS = {
    "consolidated_workflow_skill": verify_workflow_contract,
    "repository_trait_bootstrap": verify_repository_contract,
    "toml_trait_catalog": verify_catalog_contract,
    "trait_resolution": verify_resolution_contract,
    "automatic_trait_hooks": verify_automatic_hook_contract,
}


def verify_capability(name: str) -> None:
    VERIFIERS[name]()
