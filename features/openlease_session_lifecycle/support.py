"""Capability-local verification subjects for session establishment."""

from __future__ import annotations

from pathlib import Path

from features.support.coordination import CoordinationEnvironment


def environment() -> CoordinationEnvironment:
    return CoordinationEnvironment()


def registered_repositories(env: CoordinationEnvironment) -> list[str]:
    return [item["identifier"] for item in env.state()["repositories"]]


def registered_authorities(env: CoordinationEnvironment) -> list[dict]:
    return env.state()["authorities"]


def spaces(env: CoordinationEnvironment) -> list[dict]:
    return env.state()["spaces"]


def relationships(env: CoordinationEnvironment) -> tuple[list, list]:
    state = env.state()
    return state["parents"], state["dependencies"]


def claim_resolves(env: CoordinationEnvironment, session: dict) -> bool:
    """A claim for this repository resolves against the registered graph."""
    env.workspace_json(
        "claim", "--space", session["space"], "--authority", session["authority"]
    )
    return env.workspace_json("closure", "--space", session["space"])["lockable"]


def space_scoped_source(env: CoordinationEnvironment, root: Path, space: str) -> str:
    """Bind one space-scoped trait document so resolution can select it."""
    from openlease import ConfigurationLayout

    from zpp.utils.openlease import create_zpp_openlease

    document = root / "shared-tooling.toml"
    document.write_text(
        '[meta]\nselection = "all"\n\n[[trait]]\n[trait.content]\n'
        'body = "Space-scoped tooling body."\n',
        encoding="utf-8",
    )
    lifecycle = create_zpp_openlease(env.home / "openlease")
    lifecycle.bind_configuration_source(
        "zpp.traits",
        "space-tooling",
        document,
        "space",
        space,
        codec="toml",
        layout=ConfigurationLayout.DEDICATED.value,
    )
    return "Space-scoped tooling body."
