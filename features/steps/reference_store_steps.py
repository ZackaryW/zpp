"""Reference-store steps: assignment validation through the real CLI.

Only the refusal paths are exercised here. Accepting an assignment requires a
store that openspec has actually registered, which a hermetic scenario cannot
create without a test-only seam - that behaviour is covered by the unit suite
instead.
"""

import tomllib

import tomli_w
from behave import given, then, when

from trait_steps import run_cli, zpp_home


@given('a workset "{name}" with member "{member}"')
def step_workset_with_member(context, name, member):
    member_dir = context.tmp / member
    member_dir.mkdir(exist_ok=True)
    worksets_dir = zpp_home() / "worksets"
    worksets_dir.mkdir(parents=True, exist_ok=True)
    (worksets_dir / f"{name}.toml").write_text(tomli_w.dumps({
        "version": 3,
        "workspace": str(context.tmp / f"{name}.code-workspace"),
        "members": {member: {"path": str(member_dir)}},
        "profiles": {},
        "reference_stores": [],
    }))


@when('the owner assigns reference store "{store_id}" to workset "{name}"')
def step_assign(context, store_id, name):
    run_cli(context, ["workset", "assign-store", name, store_id])


@when('the owner unassigns reference store "{store_id}" from workset "{name}"')
def step_unassign(context, store_id, name):
    run_cli(context, ["workset", "unassign-store", name, store_id])


@then('workset "{name}" has no reference stores')
def step_no_reference_stores(context, name):
    side = tomllib.loads((zpp_home() / "worksets" / f"{name}.toml").read_text())
    assert side.get("reference_stores", []) == [], side.get("reference_stores")
