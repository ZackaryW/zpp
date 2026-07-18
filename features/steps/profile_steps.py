import json

import tomli_w
from behave import given, then, when

from zpp.core import governance, sidecar
from trait_steps import run_cli, zpp_home


def _sidecar(context, name="demo"):
    wsdir = zpp_home() / "worksets"
    wsdir.mkdir(parents=True, exist_ok=True)
    return wsdir / f"{name}.toml"


def _member_dir(context, member):
    d = context.tmp / member
    d.mkdir(exist_ok=True)
    return d


def _write_sidecar(context, name, members, profiles):
    data = {"version": 2,
            "workspace": str(context.tmp / f"{name}.code-workspace"),
            "members": members, "profiles": profiles}
    _sidecar(context, name).write_text(tomli_w.dumps(data))


@given('a workset "{name}" with member "{member}" and a default profile applying trait "{trait}"')
def step_default_profile_trait(context, name, member, trait):
    d = _member_dir(context, member)
    _write_sidecar(context, name, {member: {"path": str(d)}},
                   {"default": {"traits": {"apply": [trait]}}})
    context.member_path = d


@given('a workset "{name}" with member "{member}" pointing at profile "{profile}" that binds store "{store}"')
def step_pointer_profile(context, name, member, profile, store):
    d = _member_dir(context, member)
    _write_sidecar(context, name, {member: {"path": str(d), "profile": profile}},
                   {profile: {"governance": {"store": store}}})
    context.member_path = d


@given('a workset "{name}" with member "{member}" and a default profile setting zmem mode "{mode}"')
def step_default_profile_zmem(context, name, member, mode):
    d = _member_dir(context, member)
    _write_sidecar(context, name, {member: {"path": str(d)}},
                   {"default": {"zmem": {"mode": mode}}})
    context.member_path = d


@given('a workset "{name}" with member "{member}" whose default profile binds store "{store}"')
def step_default_profile_binds(context, name, member, store):
    d = _member_dir(context, member)
    _write_sidecar(context, name, {member: {"path": str(d)}},
                   {"default": {"governance": {"store": store}}})
    context.member_path = d


@given('a workset "{name}" with member "{member}" and a sidecar default profile applying trait "{trait}"')
def step_sidecar_default(context, name, member, trait):
    d = _member_dir(context, member)
    _write_sidecar(context, name, {member: {"path": str(d)}},
                   {"default": {"traits": {"apply": [trait]}}})
    context.member_path = d
    context.workspace_file = context.tmp / f"{name}.code-workspace"


@given('a shared .zpp-workset file whose default profile applies trait "{trait}"')
def step_shared_file(context, trait):
    shared = context.workspace_file.parent / (
        context.workspace_file.name.removesuffix(".code-workspace") + ".zpp-workset")
    shared.write_text(tomli_w.dumps({"profiles": {"default": {"traits": {"apply": [trait]}}}}))


@given('member "{member}" commits a zpp.toml setting zmem mode "{mode}"')
def step_repo_zmem(context, member, mode):
    (context.member_path / "zpp.toml").write_text(f'[zmem]\nmode = "{mode}"\n')


@given('member "{member}" commits a zpp.toml binding store "{store}"')
def step_repo_binds(context, member, store):
    (context.member_path / "zpp.toml").write_text(f'[governance]\nstore = "{store}"\n')


@given('the store "{store}" is registered')
def step_store_registered(context, store):
    context.registered = getattr(context, "registered", set()) | {store}
    _patch_stores(context)


@given('the stores "{stores}" are registered')
def step_stores_registered(context, stores):
    context.registered = getattr(context, "registered", set()) | {
        s.strip() for s in stores.split(",")}
    _patch_stores(context)


def _patch_stores(context):
    from zpp.core import adapter
    reg = {s: f"/stores/{s}" for s in context.registered}
    adapter.store_list = lambda: dict(reg)


@when('I resolve config for member "{member}"')
def step_resolve_config(context, member):
    context.resolved = governance.resolve_config(context.member_path)


@when('I resolve governance for member "{member}"')
def step_resolve_gov(context, member):
    context.mode = governance.resolve(context.member_path)


@then('the effective traits include "{trait}" from tier "{tier}"')
def step_traits_include(context, trait, tier):
    eff = context.resolved["effective"].get("traits", {}).get("apply", [])
    assert trait in eff, eff
    assert context.resolved["origins"].get("traits.apply", "").endswith(tier), \
        context.resolved["origins"]


@then('the effective traits do not include "{trait}"')
def step_traits_exclude(context, trait):
    eff = context.resolved["effective"].get("traits", {}).get("apply", [])
    assert trait not in eff, eff


@then('the effective zmem mode is "{mode}" from tier "{tier}"')
def step_zmem_mode(context, mode, tier):
    assert context.resolved["effective"]["zmem"]["mode"] == mode
    assert context.resolved["origins"]["zmem.mode"] == tier


@then('the governance mode is "{mode}" by rule {rule:d} with store "{store}"')
def step_gov_mode(context, mode, rule, store):
    assert context.mode["mode"] == mode, context.mode
    assert context.mode["rule"] == rule, context.mode
    assert context.mode["store"] == store, context.mode


@given('the shared concept aside, profile "{profile}" extends "{base}" and binds store "{store}"')
def step_profile_extends(context, profile, base, store):
    import tomllib
    side_path = _sidecar(context, "demo")
    data = tomllib.loads(side_path.read_text())
    data["profiles"][profile] = {"extends": base, "governance": {"store": store}}
    side_path.write_text(tomli_w.dumps(data))


@given('member "{member}" points at profile "{profile}"')
def step_member_points(context, member, profile):
    import tomllib
    side_path = _sidecar(context, "demo")
    data = tomllib.loads(side_path.read_text())
    data["members"][member]["profile"] = profile
    side_path.write_text(tomli_w.dumps(data))


@given('a shared .zpp-workset file naming a member "{member}" with profile "{profile}"')
def step_shared_phantom(context, member, profile):
    ws = context.tmp / "demo.code-workspace"
    ws.write_text('{"folders": []}')
    shared = context.tmp / "demo.zpp-workset"
    shared.write_text(tomli_w.dumps(
        {"profiles": {"default": {}}, "members": {member: {"profile": profile}}}))
    # relocated HOME makes the real openspec CLI emit a first-run notice
    # instead of JSON; fake the adapter reads so doctor exercises zpp's logic
    from zpp.core import adapter
    adapter.workset_list = lambda: {"demo": []}
    adapter.store_list = lambda: {}
