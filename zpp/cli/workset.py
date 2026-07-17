"""zpp workset - openspec composition + governance semantics."""

from pathlib import Path

import typer

from ..core import adapter, sidecar, worksets
from .common import emit, fail, only_workset

app = typer.Typer(
    no_args_is_help=True,
    help="Worksets: openspec composition + governance semantics",
)


@app.command("import")
def workset_import(
    workspace_file: Path,
    name: str = typer.Option(None, help="override the derived workset name"),
    partial: bool = typer.Option(False, help="skip member folders missing on this machine"),
):
    """Adopt a .code-workspace as a workset (layout truth stays in the file)."""
    try:
        created, members = worksets.do_import(workspace_file, name, partial)
    except (worksets.WorksetError, adapter.OpenspecError) as e:
        fail(str(e))
    typer.echo(f"imported workset '{created}' with {len(members)} member(s)")
    for m in members:
        typer.echo(f"  {m['name']}  {m['path']}")


@app.command()
def sync(
    name: str,
    yes: bool = typer.Option(False, "--yes", help="apply without confirmation (still prompts on destructive plans)"),
    plan_only: bool = typer.Option(False, "--plan", help="show the plan, apply nothing"),
):
    """One-way reconcile: workspace file -> workset + sidecar."""
    try:
        plan = worksets.sync_plan(name)
    except (worksets.WorksetError, adapter.OpenspecError) as e:
        fail(str(e))
    changes = bool(plan["added"] or plan["removed"] or plan["moved"])
    for m in plan["added"]:
        typer.echo(f"  + {m['name']}  {m['path']}")
    for n, meta in plan["removed"].items():
        bound = f"  (drops binding -> {meta['store']})" if "store" in meta else ""
        typer.echo(f"  - {n}  {meta.get('path')}{bound}")
    for m in plan["moved"]:
        typer.echo(f"  ~ {m['name']}  -> {m['path']}")
    if not changes:
        typer.echo("in sync - nothing to do")
        return
    if plan_only:
        return
    if plan["destructive"] and not typer.confirm(
        f"plan drops bindings for: {', '.join(plan['destructive'])} - continue?"
    ):
        raise typer.Exit(1)
    if not plan["destructive"] and not yes and not typer.confirm("apply?"):
        raise typer.Exit(1)
    worksets.sync_apply(name, plan)
    typer.echo("synced")


@app.command()
def bind(
    member: str,
    store_id: str,
    workset: str = typer.Option(None, help="workset name (required outside a single-workset context)"),
):
    """Record that a member is governed by a store (sidecar, personal)."""
    _bind(member, store_id, workset)


@app.command()
def unbind(member: str, workset: str = typer.Option(None)):
    """Remove a member's store binding."""
    _bind(member, None, workset)


def _bind(member: str, store_id: str | None, workset: str | None) -> None:
    name = workset or only_workset()
    try:
        worksets.bind(name, member, store_id)
    except (worksets.WorksetError, adapter.OpenspecError) as e:
        fail(str(e))
    typer.echo(f"{member} {'->' if store_id else 'unbound'} {store_id or ''}".rstrip())


@app.command("list")
def workset_list(as_json: bool = typer.Option(False, "--json")):
    """Worksets with sidecar summary."""
    known = adapter.workset_list()
    rows = []
    for name in sorted(set(known) | set(sidecar.list_names())):
        side = sidecar.load(name)
        rows.append({
            "name": name,
            "members": len(known.get(name, side.get("members", {}) if side else {})),
            "sidecar": side is not None,
            "openspec": name in known,
        })
    emit(rows, as_json, lambda rows: [
        typer.echo(f"{r['name']}  members={r['members']}"
                   f"{'' if r['sidecar'] else '  (no sidecar)'}"
                   f"{'' if r['openspec'] else '  (no openspec workset)'}")
        for r in rows
    ])


@app.command("open")
def workset_open(name: str, tool: str = typer.Option(None, help="open with this tool")):
    """Passthrough to openspec workset open."""
    try:
        adapter.workset_open(name, tool)
    except adapter.OpenspecError as e:
        fail(str(e))


@app.command("remove")
def workset_remove(name: str, yes: bool = typer.Option(False, "--yes")):
    """Remove the openspec workset, sidecar, and snapshots."""
    if not yes and not typer.confirm(f"remove workset '{name}' (sidecar + snapshots)?"):
        raise typer.Exit(1)
    try:
        worksets.remove(name)
    except adapter.OpenspecError as e:
        fail(str(e))
    typer.echo(f"removed '{name}'")


@app.command()
def status(name: str = typer.Argument(None), as_json: bool = typer.Option(False, "--json")):
    """Members, governance modes, bindings, detected store roles."""
    name = name or only_workset()
    try:
        data = worksets.status(name)
    except worksets.WorksetError as e:
        fail(str(e))

    def human(d):
        typer.echo(f"workset: {d['name']}")
        typer.echo(f"source:  {d['workspace']}")
        for m in d["members"]:
            flags = "".join([
                "" if m["exists"] else "  MISSING",
                "  [store]" if m["is_store"] else "",
                f"  -> {m['store']}" if m["store"] else "",
            ])
            typer.echo(f"  {m['name']}  {m['path']}{flags}")

    emit(data, as_json, human)


@app.command("doctor")
def workset_doctor(as_json: bool = typer.Option(False, "--json")):
    """Drift between zpp and openspec state, each finding with a fix."""
    try:
        findings = worksets.doctor()
    except adapter.OpenspecError as e:
        fail(str(e))
    if not findings:
        typer.echo("no drift found")
        return
    emit(findings, as_json, lambda fs: [
        typer.echo(f"[{f['workset']}] {f['problem']}\n    fix: {f['fix']}") for f in fs
    ])
    raise typer.Exit(1)
