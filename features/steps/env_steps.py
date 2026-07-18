import os
from pathlib import Path

from behave import given

from trait_steps import zpp_home


@given('a workset-bound repo whose workset tier applies "{workset_trait}" and whose repo tier applies "{repo_trait}"')
def step_workset_bound(context, workset_trait, repo_trait):
    member = context.tmp / "member"
    member.mkdir(exist_ok=True)
    (member / "zpp.toml").write_text(f'[traits]\napply = ["{repo_trait}"]\n')
    worksets_dir = zpp_home() / "worksets"
    worksets_dir.mkdir(parents=True, exist_ok=True)
    (worksets_dir / "demo.toml").write_text(
        f'version = 1\n'
        f'workspace = "{context.tmp / "demo.code-workspace"}"\n'
        f'[members.member]\npath = "{member}"\nstore = "gov"\n'
        f'[overlay.traits]\napply = ["{workset_trait}"]\n'
    )
    context.repo = member


@given('the session sets ZPP_TRAITS to "{value}"')
def step_set_env(context, value):
    os.environ["ZPP_TRAITS"] = value


@given('the session sets ZPP_TRAITS to ""')
def step_set_env_empty(context):
    os.environ["ZPP_TRAITS"] = ""
