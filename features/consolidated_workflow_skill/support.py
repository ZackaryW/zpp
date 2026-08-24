"""Public packaged-asset subjects for the workflow-family capability."""

from __future__ import annotations

import tomllib

from zpp.artifacts import packaged_traits, packaged_workflow_skills

EXPECTED_WORKFLOW_ENTRY_NAMES = (
    "zpp-auto",
    "zpp-new-feature",
    "zpp-fix-bug",
    "zpp-scaffold",
    "zpp-generic-workflow",
    "zpp-legacy-workflow",
)


def load_workflow_family():
    """Load the complete validated family through the package public API."""
    return packaged_workflow_skills()


def load_trait_documents() -> dict[str, dict]:
    """Decode the complete packaged trait collection."""
    return {
        item.family: tomllib.loads(item.content.decode("utf-8"))
        for item in packaged_traits()
    }
