"""Packaged ZPP source assets."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from importlib.resources import as_file, files
from typing import Final

from agent_router import Agent, Hook, Skill

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind


@dataclass(frozen=True, slots=True)
class PackagedTrait:
    family: str
    content: bytes


WORKFLOW_SKILL_ROLE: Final[str] = "workflow"
COMPANION_SKILL_ROLE: Final[str] = "companion"

WORKFLOW_ENTRY_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpp-auto",
    "zpp-new-feature",
    "zpp-fix-bug",
    "zpp-scaffold",
    "zpp-generic-workflow",
    "zpp-legacy-workflow",
)
COMPLETE_WORKFLOW_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpp-new-feature",
    "zpp-fix-bug",
    "zpp-scaffold",
    "zpp-generic-workflow",
)
WORKFLOW_KERNEL_SKILL_NAME: Final[str] = "zpps-workflow-kernel"
WORKFLOW_STAGE_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpps-clarify",
    "zpps-shape-bdd",
    "zpps-planning-ponytail",
    "zpps-mature-utilities",
    "zpps-wire",
    "zpps-form-specs",
    "zpps-finalize",
)
OPENSPEC_ADAPTER_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpps-explore",
    "zpps-new-change",
    "zpps-continue-change",
    "zpps-ff-change",
    "zpps-propose-change",
    "zpps-update-change",
    "zpps-apply-change",
    "zpps-verify-change",
    "zpps-sync-specs",
    "zpps-archive-change",
    "zpps-bulk-archive-change",
)
REPOSITORY_EVIDENCE_SKILL_NAME: Final[str] = "zpps-verify-repository"
WORKFLOW_SKILL_NAMES: Final[tuple[str, ...]] = (
    *WORKFLOW_ENTRY_SKILL_NAMES,
    WORKFLOW_KERNEL_SKILL_NAME,
    *WORKFLOW_STAGE_SKILL_NAMES,
    *OPENSPEC_ADAPTER_SKILL_NAMES,
    REPOSITORY_EVIDENCE_SKILL_NAME,
)

_SKILL_DOCUMENT = "SKILL.md"
_NUMBERED_WORKFLOW_SECTION = re.compile(r"(?m)^##\s+\d+\.\s+.+$")
_EXPLICIT_COMPONENT_USE = re.compile(r"(?m)^Use `(zpps-[a-z0-9-]+)`(?:[.,;:\s]|$)")


class PackagedSkillError(ValueError):
    pass


def workflow_stage_sections(document: str) -> tuple[tuple[str, ...], ...]:
    headings = tuple(_NUMBERED_WORKFLOW_SECTION.finditer(document))
    sections: list[tuple[str, ...]] = []
    for index, heading in enumerate(headings):
        end = (
            headings[index + 1].start() if index + 1 < len(headings) else len(document)
        )
        body = document[heading.end() : end]
        stages = tuple(
            match.group(1)
            for match in _EXPLICIT_COMPONENT_USE.finditer(body)
            if match.group(1) in WORKFLOW_STAGE_SKILL_NAMES
        )
        if stages:
            sections.append(stages)
    return tuple(sections)


def validate_workflow_stage_sequence(name: str, document: str) -> None:
    sections = workflow_stage_sections(document)
    collapsed = tuple(stages for stages in sections if len(stages) != 1)
    if collapsed:
        raise PackagedSkillError(
            f"complete workflow {name!r} must declare reusable stages in distinct "
            "numbered sections"
        )
    actual = tuple(stages[0] for stages in sections)
    missing = tuple(
        stage for stage in WORKFLOW_STAGE_SKILL_NAMES if stage not in actual
    )
    if missing:
        raise PackagedSkillError(
            f"complete workflow {name!r} is missing reusable stage(s): "
            f"{list(missing)!r}"
        )
    duplicates = tuple(
        stage for stage in WORKFLOW_STAGE_SKILL_NAMES if actual.count(stage) != 1
    )
    if duplicates:
        raise PackagedSkillError(
            f"complete workflow {name!r} must declare each reusable stage once in "
            "a distinct numbered section"
        )
    if actual != WORKFLOW_STAGE_SKILL_NAMES:
        raise PackagedSkillError(
            f"complete workflow {name!r} has invalid reusable stage order: "
            f"expected={WORKFLOW_STAGE_SKILL_NAMES!r}, actual={actual!r}"
        )


def _skill_document(skill: Skill) -> str:
    documents = tuple(
        item for item in skill.files if item.relative_path == _SKILL_DOCUMENT
    )
    if len(documents) != 1:
        raise PackagedSkillError(
            f"packaged workflow member {skill.name!r} must contain one "
            f"{_SKILL_DOCUMENT}"
        )
    return documents[0].content.decode("utf-8")


def _role_skill_names(role: str) -> tuple[str, ...]:
    root = files("zpp.artifacts").joinpath("skills", role)
    if not root.is_dir():
        raise PackagedSkillError(f"packaged skill role is missing: {role}")
    return tuple(
        sorted(
            (
                item.name
                for item in root.iterdir()
                if item.is_dir() and item.joinpath(_SKILL_DOCUMENT).is_file()
            ),
            key=lambda name: (name.casefold(), name),
        )
    )


def _load_role_skills(role: str) -> tuple[Skill, ...]:
    root = files("zpp.artifacts").joinpath("skills", role)
    loaded: list[Skill] = []
    for name in _role_skill_names(role):
        with as_file(root.joinpath(name)) as path:
            loaded.append(Skill.from_path(path))
    return tuple(loaded)


def packaged_workflow_skills() -> tuple[Skill, ...]:
    discovered = _role_skill_names(WORKFLOW_SKILL_ROLE)
    expected = frozenset(WORKFLOW_SKILL_NAMES)
    actual = frozenset(discovered)
    if actual != expected or len(discovered) != len(WORKFLOW_SKILL_NAMES):
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise PackagedSkillError(
            "packaged workflow family does not match its canonical inventory: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    root = files("zpp.artifacts").joinpath("skills", WORKFLOW_SKILL_ROLE)
    loaded: list[Skill] = []
    for name in WORKFLOW_SKILL_NAMES:
        with as_file(root.joinpath(name)) as path:
            skill = Skill.from_path(path)
        if skill.name != name:
            raise PackagedSkillError(
                f"packaged workflow member {name!r} declares name {skill.name!r}"
            )
        if name in COMPLETE_WORKFLOW_SKILL_NAMES:
            validate_workflow_stage_sequence(name, _skill_document(skill))
        loaded.append(skill)
    return tuple(loaded)


def packaged_companion_skills() -> tuple[Skill, ...]:
    loaded = _load_role_skills(COMPANION_SKILL_ROLE)
    if not loaded:
        raise PackagedSkillError("packaged companion role contains no skill")
    return loaded


def packaged_workflow_hook(agent: Agent) -> Hook:
    relative_paths = {
        Agent.CODEX: ("hooks", "codex", "zpp-traits.json"),
        Agent.CLAUDE: ("hooks", "claude", "zpp-traits.json"),
        Agent.KIMI: ("hooks", "kimi", "zpp-traits.toml"),
        Agent.PI: ("hooks", "pi", "zpp-traits.ts"),
    }
    resource = files("zpp.artifacts").joinpath(*relative_paths[agent])
    with as_file(resource) as path:
        return Hook.from_path(path, source_agent=agent)


def packaged_traits() -> tuple[PackagedTrait, ...]:
    root = files("zpp.artifacts").joinpath("traits")
    documents = sorted(
        (
            item
            for item in root.iterdir()
            if item.is_file() and item.name.endswith(".toml")
        ),
        key=lambda item: (item.name.casefold(), item.name),
    )
    return tuple(
        PackagedTrait(item.name.removesuffix(".toml"), item.read_bytes())
        for item in documents
    )


def packaged_trait_source() -> BoundTraitSource:
    documents = tuple(
        BoundTraitDocument(
            family=item.family,
            values=tomllib.loads(item.content.decode("utf-8")),
            identifier=f"zpp:packaged:{item.family}",
            order=order,
        )
        for order, item in enumerate(packaged_traits())
    )
    return BoundTraitSource(
        kind=SourceKind.GLOBAL,
        identifier="zpp:packaged",
        order=10_000,
        documents=documents,
    )


__all__ = [
    "COMPANION_SKILL_ROLE",
    "COMPLETE_WORKFLOW_SKILL_NAMES",
    "OPENSPEC_ADAPTER_SKILL_NAMES",
    "REPOSITORY_EVIDENCE_SKILL_NAME",
    "WORKFLOW_ENTRY_SKILL_NAMES",
    "WORKFLOW_KERNEL_SKILL_NAME",
    "WORKFLOW_SKILL_NAMES",
    "WORKFLOW_SKILL_ROLE",
    "WORKFLOW_STAGE_SKILL_NAMES",
    "PackagedSkillError",
    "PackagedTrait",
    "packaged_companion_skills",
    "packaged_trait_source",
    "packaged_traits",
    "packaged_workflow_hook",
    "packaged_workflow_skills",
    "validate_workflow_stage_sequence",
    "workflow_stage_sections",
]
