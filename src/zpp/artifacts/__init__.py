"""Packaged ZPP source assets."""

from __future__ import annotations

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

_SKILL_DOCUMENT = "SKILL.md"


class PackagedSkillError(ValueError):
    pass


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


def packaged_workflow_skill() -> Skill:
    loaded = _load_role_skills(WORKFLOW_SKILL_ROLE)
    if len(loaded) != 1:
        raise PackagedSkillError(
            "packaged workflow role must contain exactly one skill, "
            f"found {len(loaded)}"
        )
    return loaded[0]


def packaged_companion_skills() -> tuple[Skill, ...]:
    loaded = _load_role_skills(COMPANION_SKILL_ROLE)
    if not loaded:
        raise PackagedSkillError("packaged companion role contains no skill")
    return loaded


def packaged_workflow_hook(agent: Agent) -> Hook:
    relative_paths = {
        Agent.CODEX: ("hooks", "codex", "zpp-session.json"),
        Agent.CLAUDE: ("hooks", "claude", "zpp-session.json"),
        Agent.KIMI: ("hooks", "kimi", "zpp-session.toml"),
        Agent.PI: ("hooks", "pi", "zpp-session.ts"),
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
    "WORKFLOW_SKILL_ROLE",
    "PackagedSkillError",
    "PackagedTrait",
    "packaged_companion_skills",
    "packaged_trait_source",
    "packaged_traits",
    "packaged_workflow_hook",
    "packaged_workflow_skill",
]
