from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from agent_router import Agent, InvalidAssetError

import zpp.artifacts
from zpp.artifacts import (
    COMPANION_SKILL_ROLE,
    COMPLETE_WORKFLOW_SKILL_NAMES,
    OPENSPEC_ADAPTER_SKILL_NAMES,
    REPOSITORY_EVIDENCE_SKILL_NAME,
    WORKFLOW_ENTRY_SKILL_NAMES,
    WORKFLOW_KERNEL_SKILL_NAME,
    WORKFLOW_SKILL_NAMES,
    WORKFLOW_SKILL_ROLE,
    WORKFLOW_STAGE_SKILL_NAMES,
    PackagedSkillError,
    packaged_companion_skills,
    packaged_trait_source,
    packaged_traits,
    packaged_workflow_hook,
    packaged_workflow_reminder_hook,
    packaged_workflow_skills,
)
from zpp.core.models import SourceKind


def _write_skill(root: Path, name: str, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Author with ZPP.\n---\n{body}\n",
        newline="\n",
    )


def test_packaged_assets_are_loaded_before_resource_lifetime_ends(
    tmp_path: Path,
    monkeypatch,
) -> None:
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "z.toml").write_bytes(b"z-content")
    (traits / "a.toml").write_bytes(b"a-content")
    role = tmp_path / "skills" / WORKFLOW_SKILL_ROLE
    for name in WORKFLOW_SKILL_NAMES:
        _write_skill(role / name, name, "Run it.")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    loaded_skills = packaged_workflow_skills()
    loaded_traits = packaged_traits()

    assert tuple(skill.name for skill in loaded_skills) == WORKFLOW_SKILL_NAMES
    assert [item.family for item in loaded_traits] == ["a", "z"]
    assert [item.content for item in loaded_traits] == [
        b"a-content",
        b"z-content",
    ]


def test_packaged_companion_skills_are_detached_in_deterministic_order(
    tmp_path: Path,
    monkeypatch,
) -> None:
    companion = tmp_path / "skills" / COMPANION_SKILL_ROLE
    for name in ("zpp-configure-behave", "vendor-skill", "zpp-author-trait"):
        _write_skill(companion / name, name, name)
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    loaded = packaged_companion_skills()
    for source in companion.iterdir():
        (source / "SKILL.md").unlink()
        source.rmdir()

    assert tuple(skill.name for skill in loaded) == (
        "vendor-skill",
        "zpp-author-trait",
        "zpp-configure-behave",
    )
    assert [
        next(item.content for item in skill.files if item.relative_path == "SKILL.md")
        for skill in loaded
    ] == [
        b"---\nname: vendor-skill\ndescription: Author with ZPP.\n---\nvendor-skill\n",
        b"---\nname: zpp-author-trait\ndescription: Author with ZPP.\n---\n"
        b"zpp-author-trait\n",
        b"---\nname: zpp-configure-behave\ndescription: Author with ZPP.\n---\n"
        b"zpp-configure-behave\n",
    ]


def test_packaged_companion_role_ignores_entries_without_a_skill_document(
    tmp_path: Path,
    monkeypatch,
) -> None:
    companion = tmp_path / "skills" / COMPANION_SKILL_ROLE
    _write_skill(companion / "zpp-author-trait", "zpp-author-trait", "body")
    (companion / "notes").mkdir()
    (companion / "README.md").write_text("not a skill", newline="\n")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    assert tuple(skill.name for skill in packaged_companion_skills()) == (
        "zpp-author-trait",
    )


def test_packaged_companion_skills_fail_as_one_invalid_set(
    tmp_path: Path,
    monkeypatch,
) -> None:
    companion = tmp_path / "skills" / COMPANION_SKILL_ROLE
    _write_skill(companion / "zpp-author-trait", "zpp-author-trait", "body")
    invalid = companion / "zpp-configure-behave"
    invalid.mkdir(parents=True)
    (invalid / "SKILL.md").write_text("no frontmatter here", newline="\n")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(InvalidAssetError):
        packaged_companion_skills()


@pytest.mark.parametrize("defect", ["missing", "extra"])
def test_packaged_workflow_role_requires_exact_canonical_family(
    tmp_path: Path,
    monkeypatch,
    defect: str,
) -> None:
    role = tmp_path / "skills" / WORKFLOW_SKILL_ROLE
    names = list(WORKFLOW_SKILL_NAMES)
    if defect == "missing":
        names.pop()
    else:
        names.append("extra-workflow")
    for name in names:
        _write_skill(role / name, name, "Run it.")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(PackagedSkillError):
        packaged_workflow_skills()


def test_packaged_workflow_family_rejects_mismatched_declared_name(
    tmp_path: Path,
    monkeypatch,
) -> None:
    role = tmp_path / "skills" / WORKFLOW_SKILL_ROLE
    for name in WORKFLOW_SKILL_NAMES:
        declared = "wrong-name" if name == REPOSITORY_EVIDENCE_SKILL_NAME else name
        _write_skill(role / name, declared, "Run it.")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(PackagedSkillError, match="declares name"):
        packaged_workflow_skills()


def test_packaged_roles_fail_when_missing_or_empty(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "skills" / COMPANION_SKILL_ROLE).mkdir(parents=True)
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(PackagedSkillError):
        packaged_companion_skills()
    with pytest.raises(PackagedSkillError):
        packaged_workflow_skills()


def test_packaged_companion_inventory_binds_the_vendored_zmem_skills() -> None:
    assert tuple(skill.name for skill in packaged_companion_skills()) == (
        "zmem-author-commits",
        "zmem-query-memory",
        "zpp-author-trait",
        "zpp-configure-behave",
        "zpp-maintain-openspec",
    )


def test_packaged_authoring_skills_are_valid_cross_agent_assets() -> None:
    companions = {skill.name: skill for skill in packaged_companion_skills()}
    selected = (
        companions["zpp-author-trait"],
        companions["zpp-configure-behave"],
    )

    assert all(skill.compatible_agents == frozenset(Agent) for skill in selected)
    assert all(
        sum(item.relative_path == "SKILL.md" for item in skill.files) == 1
        for skill in selected
    )


def test_packaged_toml_becomes_a_detached_global_bound_source(
    tmp_path: Path,
    monkeypatch,
) -> None:
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "bdd.toml").write_text(
        "[meta]\nselection = 'first-win'\n"
        "[[trait]]\n[trait.content]\nbody = 'packaged bdd'\n"
    )
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    source = packaged_trait_source()

    assert source.kind is SourceKind.GLOBAL
    assert source.identifier == "zpp:packaged"
    assert [item.family for item in source.documents] == ["bdd"]
    assert source.documents[0].values["meta"] == {"selection": "first-win"}


def test_packaged_assets_have_exact_workflow_and_trait_inventories() -> None:
    traits = packaged_traits()
    families = {item.family for item in traits}

    assert "workflow" not in families
    assert "automatic-workflow" not in families
    assert "workflow-authority" not in families
    assert families == {
        "bdd",
        "bdd-execution",
        "bdd-structure",
        "tdd",
        "tooling",
    }

    skills = packaged_workflow_skills()
    assert tuple(skill.name for skill in skills) == WORKFLOW_SKILL_NAMES
    assert WORKFLOW_ENTRY_SKILL_NAMES == (
        "zpp-auto",
        "zpp-new-feature",
        "zpp-fix-bug",
        "zpp-scaffold",
        "zpp-generic-workflow",
        "zpp-legacy-workflow",
    )
    assert COMPLETE_WORKFLOW_SKILL_NAMES == (
        "zpp-new-feature",
        "zpp-fix-bug",
        "zpp-scaffold",
        "zpp-generic-workflow",
    )
    assert (
        *WORKFLOW_ENTRY_SKILL_NAMES,
        WORKFLOW_KERNEL_SKILL_NAME,
        *WORKFLOW_STAGE_SKILL_NAMES,
        *OPENSPEC_ADAPTER_SKILL_NAMES,
        REPOSITORY_EVIDENCE_SKILL_NAME,
    ) == WORKFLOW_SKILL_NAMES
    assert len(skills) == 26
    assert len(OPENSPEC_ADAPTER_SKILL_NAMES) == 11
    assert not {
        "zpp-workflow",
        "zpps-onboard",
        "zpps-plan-change",
        "zpps-verify",
        "zpps-archive",
    } & set(WORKFLOW_SKILL_NAMES)


def test_packaged_skills_compose_compact_runtime_contract_guidance() -> None:
    documents = {
        skill.name: next(
            item.content.decode("utf-8")
            for item in skill.files
            if item.relative_path == "SKILL.md"
        )
        for skill in packaged_workflow_skills()
    }

    for name in COMPLETE_WORKFLOW_SKILL_NAMES:
        document = documents[name]
        assert (
            f"zpp workflow run start {name} --root <root> --change <change>" in document
        )
        assert "## Registered execution" in document
        assert "## Visible stage progression invariant" not in document
        assert all(f"\n## {number}." not in document for number in range(1, 10))

    for name in (
        WORKFLOW_KERNEL_SKILL_NAME,
        *WORKFLOW_STAGE_SKILL_NAMES,
        *OPENSPEC_ADAPTER_SKILL_NAMES,
        REPOSITORY_EVIDENCE_SKILL_NAME,
    ):
        document = documents[name]
        assert document.count("validated packaged JSON contract") == 1
        assert "On any mismatch, return `component-mismatch`" not in document

    assert "mandatory workflow registration" in documents["zpp-auto"]
    assert "without creating workflow reminder state" in documents["zpp-auto"]
    assert (
        "Invoke `zpp-generic-workflow` exactly once" in documents["zpp-legacy-workflow"]
    )


def test_packaged_bdd_authority_rejects_non_behavioral_evidence() -> None:
    documents = {
        skill.name: next(
            item.content.decode("utf-8")
            for item in skill.files
            if item.relative_path == "SKILL.md"
        )
        for skill in packaged_workflow_skills()
    }
    shaping = documents["zpps-shape-bdd"]
    verification = documents["zpps-verify-change"]

    for rejected in (
        "Literal-text matching",
        "self-recording steps",
        "execution-only checks",
        "pure occurrence or collection counts",
        "shared capability-wide assertions",
    ):
        assert rejected in shaping
    assert "cannot be the scenario's sole public-system observation" in shaping
    assert "counts only as supplemental constraints" in verification


def test_packaged_bdd_authority_keeps_trace_on_feature_side_only() -> None:
    workflows = {
        skill.name: next(
            item.content.decode("utf-8")
            for item in skill.files
            if item.relative_path == "SKILL.md"
        )
        for skill in packaged_workflow_skills()
    }
    companions = {
        skill.name: {
            item.relative_path: item.content.decode("utf-8") for item in skill.files
        }
        for skill in packaged_companion_skills()
    }

    assert "feature-side declaration is the complete trace" in workflows[
        "zpps-form-specs"
    ]
    assert "no scenario corresponding to that BDD example" in workflows[
        "zpps-sync-specs"
    ]
    assert "no corresponding OpenSpec scenario" in workflows["zpps-verify-change"]
    assert "no corresponding OpenSpec scenario" in workflows["zpps-archive-change"]
    assert "no corresponding OpenSpec scenario" in workflows[
        "zpps-bulk-archive-change"
    ]
    assert "no corresponding OpenSpec scenario" in workflows["zpps-apply-change"]

    maintenance = companions["zpp-maintain-openspec"]
    assert "OpenSpec retains no surrogate" in maintenance["SKILL.md"]
    assert "Preserve every full OpenSpec WHEN/THEN scenario" in maintenance[
        "SKILL.md"
    ]
    assert "do not retain a target-form surrogate" in maintenance[
        "references/maintenance-contract.md"
    ]


def test_packaged_collection_has_contextual_execution_and_tool_facets() -> None:
    documents = {
        item.family: tomllib.loads(item.content.decode("utf-8"))
        for item in packaged_traits()
    }

    assert [
        flavor.get("facet", {}).get("bdd_mode")
        for flavor in documents["bdd-execution"]["trait"]
    ] == ["manual", "disabled", "complete", "targeted", None]
    assert all(
        flavor["content"]["body"].strip()
        for flavor in documents["bdd-execution"]["trait"]
    )
    assert [
        flavor["facet"]["language"] for flavor in documents["bdd-structure"]["trait"]
    ] == ["python", "flutter", "typescript"]
    assert [flavor["facet"]["tool"] for flavor in documents["tooling"]["trait"]] == [
        "rg",
        "jq",
    ]


@pytest.mark.parametrize("agent", tuple(Agent))
def test_packaged_workflow_hook_is_typed_and_resolves_for_its_agent(
    agent: Agent,
) -> None:
    hook = packaged_workflow_hook(agent)
    payload = repr(hook.fragment) + "".join(
        item.content.decode("utf-8") for item in hook.files
    )

    assert hook.name == "zpp-traits"
    assert hook.compatible_agents == frozenset({agent})
    assert f'"--agent", "{agent.value}"' in payload or (
        f"--agent {agent.value} ." in payload
    )
    assert "guard" not in payload
    assert "UserPromptSubmit" not in payload
    assert "behave" not in payload


def test_packaged_hooks_cover_post_compaction_without_duplicate_paths() -> None:
    for agent in (Agent.CODEX, Agent.CLAUDE):
        hook = packaged_workflow_hook(agent)

        assert list(hook.fragment) == ["SessionStart"]
        assert "matcher" not in hook.fragment["SessionStart"][0]

    kimi_hook = packaged_workflow_hook(Agent.KIMI)

    assert kimi_hook.fragment == [
        {
            "event": "SessionStart",
            "command": "zpp resolve --agent kimi .",
        },
        {
            "event": "PostCompact",
            "command": "zpp resolve --agent kimi .",
        },
    ]

    pi_hook = packaged_workflow_hook(Agent.PI)
    pi_source = pi_hook.files[0].content.decode("utf-8")

    assert pi_source.count('pi.on("before_agent_start"') == 1
    assert 'pi.on("session_compact"' not in pi_source


@pytest.mark.parametrize("agent", (Agent.CODEX, Agent.CLAUDE))
def test_packaged_prompt_reminder_hook_is_separate_and_read_only(
    agent: Agent,
) -> None:
    hook = packaged_workflow_reminder_hook(agent)

    assert hook is not None
    assert hook.name == "zpp-workflow-reminder"
    assert hook.compatible_agents == frozenset({agent})
    assert list(hook.fragment) == ["UserPromptSubmit"]
    payload = repr(hook.fragment)
    assert "zpp workflow run remind ." in payload
    assert "record" not in payload


@pytest.mark.parametrize("agent", (Agent.KIMI, Agent.PI))
def test_packaged_prompt_reminder_hook_omits_unconfirmed_adapters(
    agent: Agent,
) -> None:
    assert packaged_workflow_reminder_hook(agent) is None
