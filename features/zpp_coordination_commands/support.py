"""Capability-local verification subjects for the ZPP coordination surface."""

from __future__ import annotations

from pathlib import Path

from features.support.coordination import CoordinationEnvironment
from zpp.artifacts import packaged_companion_skills

SKILL = "zpp-workspace-management"
PROVIDER_TOKENS = ("openlease --help", "`openlease`", "openlease.exe")


def environment() -> CoordinationEnvironment:
    return CoordinationEnvironment()


def workspace_guidance() -> str:
    """The packaged guidance an agent reads before coordinating."""
    skill = next(item for item in packaged_companion_skills() if item.name == SKILL)
    root = Path(skill.path)
    documents = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    return "\n".join(item.read_text(encoding="utf-8") for item in documents)


def names_provider_executable(text: str) -> bool:
    return any(token in text for token in PROVIDER_TOKENS)


def state_signature(env: CoordinationEnvironment) -> str:
    state = env.state()
    return repr(
        [
            [item["identifier"] for item in state["repositories"]],
            [item["identifier"] for item in state["authorities"]],
            [item["identifier"] for item in state["spaces"]],
            state["leases"],
        ]
    )
