from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from agent_router import Agent, InvalidAssetError

import zpp.artifacts
from zpp.artifacts import (
    COMPANION_SKILL_ROLE,
    WORKFLOW_SKILL_ROLE,
    PackagedSkillError,
    packaged_companion_skills,
    packaged_trait_source,
    packaged_traits,
    packaged_workflow_hook,
    packaged_workflow_skill,
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
    skill = tmp_path / "skills" / WORKFLOW_SKILL_ROLE / "zpp-workflow"
    skill.mkdir(parents=True)
    _write_skill(skill, "zpp-workflow", "Run it.")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    loaded_skill = packaged_workflow_skill()
    loaded_traits = packaged_traits()

    assert loaded_skill.name == "zpp-workflow"
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


def test_packaged_workflow_role_requires_exactly_one_skill(
    tmp_path: Path,
    monkeypatch,
) -> None:
    role = tmp_path / "skills" / WORKFLOW_SKILL_ROLE
    for name in ("zpp-workflow", "extra-workflow"):
        _write_skill(role / name, name, "Run it.")
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(PackagedSkillError):
        packaged_workflow_skill()


def test_packaged_roles_fail_when_missing_or_empty(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "skills" / COMPANION_SKILL_ROLE).mkdir(parents=True)
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    with pytest.raises(PackagedSkillError):
        packaged_companion_skills()
    with pytest.raises(PackagedSkillError):
        packaged_workflow_skill()


def test_packaged_companion_inventory_binds_the_vendored_zmem_skills() -> None:
    assert tuple(skill.name for skill in packaged_companion_skills()) == (
        "zmem-author-commits",
        "zmem-query-memory",
        "zpp-author-trait",
        "zpp-configure-behave",
        "zpp-maintain-openspec",
    )


def test_packaged_authoring_skill_guidance_is_complete_and_cross_agent() -> None:
    companions = {skill.name: skill for skill in packaged_companion_skills()}
    trait = companions["zpp-author-trait"]
    configure = companions["zpp-configure-behave"]

    assert configure.compatible_agents == trait.compatible_agents == frozenset(Agent)
    configure_text = next(
        item.content.decode("utf-8")
        for item in configure.files
        if item.relative_path == "SKILL.md"
    )
    trait_text = next(
        item.content.decode("utf-8")
        for item in trait.files
        if item.relative_path == "SKILL.md"
    )
    assert all(
        marker in configure_text
        for marker in (
            "zpp behave init",
            "`argv`, `nx`, or `go-task`",
            "{targets}",
            "zpp-workflow",
            "Never invent executable",
            "false-negative exclusion",
        )
    )
    assert all(
        marker in trait_text
        for marker in (
            "zpp trait init",
            "zpp resolve TARGET --trait FAMILY",
            "`first-win`",
            "`all`",
            "`extend`",
            "`automatic`",
            "`manual`",
            "`always-run`",
            "repository-overwrite",
            "[[trait.when]]",
            "complete `[trait.content].body`",
        )
    )
    assert "TODO" not in configure_text
    assert "TODO" not in trait_text


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


def test_packaged_assets_keep_workflow_authority_out_of_traits() -> None:
    traits = packaged_traits()
    families = {item.family for item in traits}

    assert "workflow" not in families
    assert "automatic-workflow" not in families
    assert "workflow-authority" not in families
    assert families == {
        "bdd",
        "bdd-execution",
        "bdd-structure",
        "build",
        "dependencies",
        "tdd",
        "tooling",
        "zero-assumptions",
    }

    skill = packaged_workflow_skill()
    document = next(
        item.content for item in skill.files if item.relative_path == "SKILL.md"
    )
    text = document.decode("utf-8")
    assert "Automatic progression" in text
    assert "Traits advise the selected stage" in text
    assert "Reconcile the complete agreement" in text
    assert "A recommendation is not confirmation" in text
    assert "skipped: not applicable" in text
    assert "zpp behave" in text
    assert "bdd-execution" in text
    assert "zpp-workflow" in text
    assert "zpp-flow-wire-feature" not in text


def test_packaged_collection_has_precise_execution_activation_and_tools() -> None:
    documents = {
        item.family: tomllib.loads(item.content.decode("utf-8"))
        for item in packaged_traits()
    }

    assert documents["zero-assumptions"]["meta"]["activation"] == "always-run"
    assert [
        flavor.get("facet", {}).get("bdd_mode")
        for flavor in documents["bdd-execution"]["trait"]
    ] == ["manual", "disabled", "complete", "targeted", None]
    bodies = [
        flavor["content"]["body"] for flavor in documents["bdd-execution"]["trait"]
    ]
    assert "--gate zpp-workflow" in bodies[3]
    assert "--gate zpp-workflow" in bodies[4]
    assert all("zpp-flow-" not in body for body in bodies)
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
