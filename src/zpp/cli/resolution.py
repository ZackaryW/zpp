from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import MappingProxyType
from typing import Annotated

import typer
from agent_router import Agent

from zpp.artifacts import packaged_trait_source
from zpp.cli.shared import agent_router, emit_json, user_action
from zpp.core.application import TraitApplication, TraitInvocation
from zpp.core.evidence import EvidenceRuntime
from zpp.core.rendering import render_prompt_bodies
from zpp.utils.agent_router import active_trait_sources
from zpp.utils.agent_selection import AgentSelectionError, select_one_agent
from zpp.utils.bundler import BundlerDocuments


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

    del ctx
    documents = BundlerDocuments()
    repository = user_action(lambda: documents.read_repository(root))
    store_sources = user_action(lambda: documents.read_store_chain(root))
    plugin_sources = (
        ()
        if selected_agent is None
        else user_action(
            lambda: active_trait_sources(agent_router(selected_agent, root))
        )
    )
    sources = (
        repository.source,
        *store_sources,
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
                "explanation": dict(result.explanation),
            }
        )
        return
    typer.echo(render_prompt_bodies(result.resolution), nl=False)
