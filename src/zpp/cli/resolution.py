from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import MappingProxyType
from typing import Annotated

import typer
from agent_router import Agent

from zpp.artifacts import packaged_trait_source
from zpp.cli.shared import agent_router, emit_json, runtime, user_action
from zpp.core.application import TraitApplication, TraitInvocation
from zpp.core.evidence import EvidenceRuntime
from zpp.core.rendering import render_prompt_bodies
from zpp.utils.agent_router import active_trait_sources
from zpp.utils.agent_selection import AgentSelectionError, select_one_agent
from zpp.utils.coordination import OpenLeaseCoordination
from zpp.utils.openlease import create_trait_documents, create_zpp_openlease


def _facets(values: list[str] | None) -> MappingProxyType:
    parsed: dict[str, str | tuple[str, ...]] = {}
    for value in values or ():
        key, separator, item = value.partition("=")
        if not separator or not key or not item:
            raise typer.BadParameter(
                "facets must use non-empty NAME=VALUE syntax",
                param_hint="--facet",
            )
        prior = parsed.get(key)
        if prior is None:
            parsed[key] = item
        elif isinstance(prior, str):
            if prior != item:
                parsed[key] = (prior, item)
        elif item not in prior:
            parsed[key] = (*prior, item)
    return MappingProxyType(parsed)


def resolve(
    ctx: typer.Context,
    target: Annotated[
        Path,
        typer.Argument(help="Existing repository directory to resolve."),
    ] = Path("."),
    stage: Annotated[
        str | None,
        typer.Option("--stage", help="Explicit workflow stage for this invocation."),
    ] = None,
    facet: Annotated[
        list[str] | None,
        typer.Option("--facet", help="Known NAME=VALUE facet; repeat as needed."),
    ] = None,
    trait: Annotated[
        list[str] | None,
        typer.Option(
            "--trait",
            help="Resolve only this trait family; repeat to request several.",
        ),
    ] = None,
    agent: Annotated[
        list[Agent] | None,
        typer.Option(
            "--agent",
            help="Include at most one invoking agent's active trait artifacts.",
        ),
    ] = None,
    space: Annotated[
        str | None,
        typer.Option(
            "--space",
            help="Include sources from one selected OpenLease space.",
        ),
    ] = None,
    authority: Annotated[
        str | None,
        typer.Option(
            "--authority",
            help="Resolve selected-space sources for one authority target.",
        ),
    ] = None,
    explain: Annotated[
        bool,
        typer.Option("--explain", help="Include deterministic selection evidence."),
    ] = False,
) -> None:
    """Resolve repository, invoking-agent, and packaged trait sources."""
    root = target.resolve()
    if not root.is_dir():
        raise typer.BadParameter(
            "target must be an existing directory", param_hint="target"
        )
    try:
        selected_agent = select_one_agent(tuple(agent or ()), required=False)
    except AgentSelectionError as error:
        raise typer.BadParameter(str(error), param_hint="--agent") from error

    documents = create_trait_documents(runtime(ctx).state_root)
    repository = user_action(lambda: documents.read_repository(root))
    selected_space = space or os.environ.get("OPENLEASE_SPACE")
    session_note: str | None = None
    if selected_space is None:
        selected_space, session_note = _establish_session(runtime(ctx).state_root, root)
    if authority is not None and selected_space is None:
        raise typer.BadParameter(
            "--authority requires an established session, --space, or OPENLEASE_SPACE",
            param_hint="--authority",
        )
    space_sources = (
        ()
        if selected_space is None
        else user_action(
            lambda: documents.read_space_sources(
                root,
                selected_space,
                authority=authority,
            )
        )
    )
    plugin_sources = (
        ()
        if selected_agent is None
        else user_action(
            lambda: active_trait_sources(agent_router(selected_agent, root))
        )
    )
    sources = (
        repository.source,
        *space_sources,
        *plugin_sources,
        packaged_trait_source(),
    )
    application = TraitApplication(
        lambda selected: EvidenceRuntime(
            selected,
            Path.read_bytes,
            shutil.which,
        )
    )
    result = user_action(
        lambda: application.resolve(
            TraitInvocation(
                target=root,
                stage=stage,
                facets=_facets(facet),
                stored_context=os.environ.get("ZPP_CONTEXT"),
                repository_context=repository.context,
                sources=sources,
                requested_families=(tuple(trait) if trait is not None else None),
            )
        )
    )
    if explain:
        emit_json(
            {
                "bodies": [
                    {
                        "family": body.family,
                        "body": body.body,
                        "source": body.source.identifier,
                        "flavor": body.flavor_position,
                    }
                    for body in result.bodies
                ],
                "ZPP_CONTEXT": result.context,
                "session": selected_space,
                "session_note": session_note,
                "explanation": dict(result.explanation),
            }
        )
        return
    typer.echo(render_prompt_bodies(result.resolution), nl=False)


def _establish_session(state_root: Path, root: Path) -> tuple[str | None, str | None]:
    """Establish this worktree's session so space-scoped sources resolve.

    Resolution is read-only and must keep working outside a Git worktree, so a
    directory that cannot hold a session resolves its repository, agent, and
    packaged sources and reports why no session was established.
    """
    coordination = OpenLeaseCoordination(create_zpp_openlease(state_root))
    try:
        return coordination.establish_session(root).space_id, None
    except Exception as error:  # reported to the caller, never silently dropped
        return None, f"{type(error).__name__}: {error}"
