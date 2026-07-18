import json
import os
from pathlib import Path

from behave import given, then

from environment import make_fake_saucepan_release
from trait_steps import _trait_rows, zpp_home


@given("a fake saucepan release is served at a file URL")
def step_fake_release(context):
    os.environ["ZPP_SAUCEPAN_URL"] = make_fake_saucepan_release(context)


@given('a repo configured with saucepan mode "{mode}"')
def step_repo_saucepan_mode(context, mode):
    repo = context.tmp / "repo"
    repo.mkdir(exist_ok=True)
    (repo / "zpp.toml").write_text(f'[traits]\nsaucepan = "{mode}"\n')
    context.repo = repo


@given("saucepan is absent from PATH")
def step_no_saucepan_on_path(context):
    empty = context.tmp / "empty-bin"
    empty.mkdir(exist_ok=True)
    os.environ["PATH"] = str(empty)


@then("a managed saucepan binary exists under the zpp home")
def step_managed_binary_exists(context):
    binary = zpp_home() / "bin" / "saucepan"
    assert binary.is_file() and os.access(binary, os.X_OK), binary


@then("no managed saucepan binary exists under the zpp home")
def step_no_managed_binary(context):
    assert not (zpp_home() / "bin" / "saucepan").exists()


@then('the listing shows "{name}" from "{source}" at version "{version}"')
def step_listed_with_version(context, name, source, version):
    rows = [r for r in _trait_rows(context) if r["name"] == name]
    assert rows and rows[0]["source"] == source and rows[0]["version"] == version, rows
