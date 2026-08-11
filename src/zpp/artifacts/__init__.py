"""Packaged ZPP source assets."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib.resources import as_file, files

from agent_router import Agent, Hook, Skill

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind


@dataclass(frozen=True, slots=True)
class PackagedTrait:
    family: str
    content: bytes


def packaged_workflow_skill() -> Skill:
    resource = files("zpp.artifacts").joinpath("skills", "zpp-workflow")
    with as_file(resource) as path:
        return Skill.from_path(path)


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
    "PackagedTrait",
    "packaged_trait_source",
    "packaged_traits",
    "packaged_workflow_hook",
    "packaged_workflow_skill",
]
