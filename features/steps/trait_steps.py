"""Steps exercise the real CLI in-process via typer's test runner - every
Then asserts observed output or exit codes, never source text."""

import json
import os
import shlex
from pathlib import Path

from behave import given, then, when
from typer.testing import CliRunner

from zpp.cli import app

runner = CliRunner()


def zpp_home() -> Path:
    return Path(os.environ["ZPP_HOME"])


def run_cli(context, argv: list[str]):
    context.result = runner.invoke(app, argv)


# --- givens ---


@given('a user trait "{name}" with content "{content}"')
def step_user_trait(context, name, content):
    user_dir = zpp_home() / "user"
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / f"{name}.md").write_text(content + "\n")


@given('a saucepan pack "{pack}" containing trait "{name}" with content "{content}"')
def step_saucepan_trait(context, pack, name, content):
    pack_dir = zpp_home() / "saucepan" / pack
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / f"{name}.md").write_text(content + "\n")


@given('a saucepan pack "{pack}" at version "{version}" containing trait "{name}"')
def step_saucepan_versioned(context, pack, version, name):
    pack_dir = zpp_home() / "saucepan" / pack
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / f"{name}.md").write_text(f"content of {name}\n")
    (pack_dir / "sauce.json").write_text(
        json.dumps({"name": pack, "version": version, "description": "test pack"})
    )


@given('a repo applying traits "{names}"')
def step_repo_applying(context, names):
    repo = context.tmp / "repo"
    repo.mkdir(exist_ok=True)
    apply_list = ", ".join(f'"{n.strip()}"' for n in names.split(","))
    (repo / "zpp.toml").write_text(f"[traits]\napply = [{apply_list}]\n")
    context.repo = repo


# --- whens ---


@when('I run "zpp {args}"')
def step_run(context, args):
    run_cli(context, shlex.split(args))


@when('I run "zpp {args}" against that repo')
def step_run_against_repo(context, args):
    run_cli(context, [*shlex.split(args), str(context.repo)])


# --- thens ---


@then("the command succeeds")
def step_succeeds(context):
    assert context.result.exit_code == 0, context.result.output


@then("the command fails")
def step_fails(context):
    assert context.result.exit_code != 0, context.result.output


@then('the output contains "{text}"')
def step_output_contains(context, text):
    assert text in context.result.output, context.result.output


@then('the output does not contain "{text}"')
def step_output_not_contains(context, text):
    assert text not in context.result.output, context.result.output


def _trait_rows(context) -> list[dict]:
    result = runner.invoke(app, ["trait", "list", "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


@then('trait "{name}" is listed with source "{source}"')
def step_listed_with_source(context, name, source):
    rows = [r for r in _trait_rows(context) if r["name"] == name and not r.get("shadowed")]
    assert rows and rows[0]["source"] == source, rows


@then('the saucepan copy of "{name}" is listed as shadowed')
def step_listed_shadowed(context, name):
    rows = [r for r in _trait_rows(context)
            if r["name"] == name and r["source"] == "saucepan"]
    assert rows and rows[0]["shadowed"], rows


@then('traits "{names}" are listed with source "{source}"')
def step_all_listed(context, names, source):
    rows = {r["name"]: r for r in _trait_rows(context) if not r.get("shadowed")}
    for name in [n.strip() for n in names.split(",")]:
        assert name in rows and rows[name]["source"] == source, (name, rows.keys())


@then('the output warns about unknown trait "{name}"')
def step_warns_unknown(context, name):
    err = getattr(context.result, "stderr", "") or ""
    out = context.result.output + err
    assert "unknown" in out.lower() and name in out, out


@then('the output contains the content of builtin trait "{name}"')
def step_contains_builtin_content(context, name):
    show = runner.invoke(app, ["trait", "show", name])
    assert show.exit_code == 0, show.output
    marker = show.output.strip().splitlines()[0]
    assert marker in context.result.output, context.result.output
