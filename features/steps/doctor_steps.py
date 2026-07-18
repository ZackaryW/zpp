import os

from behave import given


def _self_governed(context):
    repo = context.tmp / "doctor-repo"
    (repo / "openspec").mkdir(parents=True, exist_ok=True)
    context.repo = repo
    return repo


@given('a self-governed repo whose zpp.toml sets doctor exclude to "{cmd}"')
def step_doctor_exclude(context, cmd):
    repo = _self_governed(context)
    (repo / "zpp.toml").write_text(f'[doctor]\nexclude = ["{cmd}"]\n')


@given('a self-governed repo whose store tier adds doctor tool "{a}" and whose repo tier adds doctor tool "{b}"')
def step_doctor_tier_union(context, a, b):
    repo = _self_governed(context)
    (repo / "zpp.default.toml").write_text(
        f'[[doctor.more]]\nwhich = "{a}"\nsuccessnote = "from store"\n'
    )
    (repo / "zpp.toml").write_text(
        f'[[doctor.more]]\nwhich = "{b}"\nsuccessnote = "from repo"\n'
    )


@given('a self-governed repo whose repo tier adds doctor tool "{cmd}" with note "{note}"')
def step_doctor_more(context, cmd, note):
    repo = _self_governed(context)
    (repo / "zpp.toml").write_text(
        f'[[doctor.more]]\nwhich = "{cmd}"\nsuccessnote = "{note}"\n'
    )


@given("a repo with an invalid zpp.toml")
def step_invalid_config(context):
    repo = _self_governed(context)
    (repo / "zpp.toml").write_text("[doctor\nthis is not toml")


@given("PATH is emptied so every tool is missing")
def step_empty_path(context):
    empty = context.tmp / "empty-bin"
    empty.mkdir(exist_ok=True)
    os.environ["PATH"] = str(empty)
