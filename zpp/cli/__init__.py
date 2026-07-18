"""zpp - zack's project protocol. Typer tree mirrors the protocol:
workset/snapshot/config sub-apps; resolve/bootstrap/doctor at root."""

import typer

from . import config, root, snapshot, trait, workset

app = typer.Typer(no_args_is_help=True, help=__doc__)
app.add_typer(workset.app, name="workset")
app.add_typer(snapshot.app, name="snapshot")
app.add_typer(config.app, name="config")
app.add_typer(trait.app, name="trait")
app.command()(root.resolve)
app.command()(root.bootstrap)
app.command()(root.doctor)
