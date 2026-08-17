"""Capability-local verification subjects for the consolidated workflow skill."""

from __future__ import annotations

import tomllib

from zpp.artifacts import packaged_traits, packaged_workflow_skill

STANDARD_COLLECTION = frozenset(
    {
        "bdd",
        "bdd-execution",
        "bdd-structure",
        "build",
        "dependencies",
        "tdd",
        "tooling",
        "zero-assumptions",
    }
)

WORKFLOW_AUTHORITY_FAMILIES = frozenset(
    {"workflow", "automatic-workflow", "workflow-authority"}
)


def load_skill():
    return packaged_workflow_skill()


def load_trait_documents() -> dict[str, dict]:
    return {
        item.family: tomllib.loads(item.content.decode("utf-8"))
        for item in packaged_traits()
    }
