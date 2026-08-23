from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import emit_json, user_action
from zpp.utils.bundler import BundlerDocuments

app = typer.Typer(
    help="Initialize exact repository trait attachments through Bundler.",
    no_args_is_help=True,
)


@app.command("init")
def initialize(
    ctx: typer.Context,
    document: Annotated[
        str,
        typer.Argument(help="The context document or one trait-family name."),
    ],
    target: Annotated[
        Path,
        typer.Argument(help="Exact repository target."),
    ] = Path("."),
) -> None:
    """Initialize only the requested context or trait-family document."""
    root = target.resolve()
    del ctx
    documents = BundlerDocuments()
    if document == "context":
        created = user_action(lambda: documents.initialize_context(root))
    else:
        created = user_action(
            lambda: documents.initialize_trait(
                root,
                document,
                {
                    "meta": {"selection": "first-win"},
                    "trait": [{"content": {"body": "Replace with complete guidance."}}],
                },
            )
        )
    emit_json({"document": str(created.path), "family": created.family})
