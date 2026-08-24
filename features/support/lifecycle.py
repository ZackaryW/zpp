"""Reusable lifecycle fixtures for capability-local Behave support."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from agent_router import Agent, AgentRouter, Hook, Scope

from zpp.artifacts import packaged_workflow_hook

FORMER_WORKFLOW_HOOK_NAME = "zpp-session"


def former_workflow_hook(agent: Agent) -> Hook:
    """Return the exact former ownership identity for the packaged hook."""
    return replace(packaged_workflow_hook(agent), name=FORMER_WORKFLOW_HOOK_NAME)


def replace_current_hook_with_former(
    router: AgentRouter,
    agent: Agent,
    *,
    scope: Scope,
    project_root: Path | None = None,
) -> Hook:
    """Replace an intact current fixture with its former owned identity."""
    current = packaged_workflow_hook(agent)
    removed = router.uninstall_hook(
        current.name,
        scope=scope,
        project_root=project_root,
    )
    assert removed.status == "removed", removed.to_dict()
    former = former_workflow_hook(agent)
    installed = router.install_hook(
        former,
        scope=scope,
        project_root=project_root,
    )
    assert installed.status == "installed", installed.to_dict()
    return former


def hook_ownership_states(
    router: AgentRouter,
    agent: Agent,
    *,
    scope: Scope,
    project_root: Path | None = None,
) -> tuple[str, str]:
    """Return current and former hook ownership states in that order."""
    current = router.inspect_hook(
        packaged_workflow_hook(agent),
        scope=scope,
        project_root=project_root,
    )
    former = router.inspect_hook(
        former_workflow_hook(agent),
        scope=scope,
        project_root=project_root,
    )
    return current.status, former.status
