from __future__ import annotations

import support
from behave import given, then, when


@given("a disposable Git worktree matching no registered repository")
def unregistered_worktree(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree()


@given("a disposable Git worktree whose session was already established")
@given("a disposable Git worktree with an established session")
@given("a disposable Git worktree with a registered repository")
@given("a disposable Git worktree with an established default session")
def established_worktree(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree()
    context.session = context.env.workspace_json("session", str(context.worktree))


@given(
    "a disposable Git worktree and an environment supplying no OpenLease session token"
)
def worktree_without_token(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree()
    context.env.runner.env = {"OPENLEASE_SESSION_TOKEN": ""}


@given(
    "a disposable Git worktree with an established session "
    "contributing a space-scoped trait source"
)
def worktree_with_space_source(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree()
    context.session = context.env.workspace_json("session", str(context.worktree))
    context.expected_body = support.space_scoped_source(
        context.env, context.worktree, context.session["space"]
    )


@given("two registered repositories with no declared relationship between them")
def two_unrelated_repositories(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree("first")
    context.other = context.env.worktree("second")
    context.session = context.env.workspace_json("session", str(context.worktree))
    context.other_session = context.env.workspace_json("session", str(context.other))


@given(
    "two registered repositories with an explicitly declared dependency relationship"
)
def two_related_repositories(context) -> None:
    two_unrelated_repositories(context)
    context.env.workspace_json(
        "relate",
        "--child",
        context.session["repository"],
        "--dependency",
        context.other_session["authority"],
        "--access",
        "read_only",
    )


@when("ZPP establishes the session for that worktree")
def establish_session(context) -> None:
    context.session = context.env.workspace_json("session", str(context.worktree))


@when("ZPP establishes the session for that worktree again")
def establish_session_again(context) -> None:
    context.second = context.env.workspace_json("session", str(context.worktree))


@when("ZPP is invoked again for that worktree without an explicit session name")
def establish_session_repeat(context) -> None:
    context.second = context.env.workspace_json("session", str(context.worktree))


@when("a caller establishes a session for that worktree under an explicit session name")
def establish_named_session(context) -> None:
    context.named = context.env.workspace_json(
        "session", str(context.worktree), "--session", "review"
    )


@when("traits resolve with no explicit space argument and no space environment value")
def resolve_without_space(context) -> None:
    context.resolution = context.env.resolve_json(str(context.worktree))


@when("a session for the first repository claims the second repository")
def claim_other_repository(context) -> None:
    context.claim = context.env.workspace(
        "claim",
        "--space",
        context.session["space"],
        "--repository",
        context.other_session["repository"],
    )
    if context.claim.exit_code == 0:
        context.closure = context.env.workspace(
            "closure", "--space", context.session["space"]
        )


@then("the worktree is registered with one worktree-covering authority")
def registered_with_authority(context) -> None:
    authorities = support.registered_authorities(context.env)
    assert support.registered_repositories(context.env) == [
        context.session["repository"]
    ]
    assert [item["relative_path"] for item in authorities] == ["."]


@then("an affected claim for that repository resolves against the authority graph")
def claim_resolves(context) -> None:
    assert support.claim_resolves(context.env, context.session) is True


@then("the existing repository and authority records are reused")
def registration_reused(context) -> None:
    assert context.second == context.session


@then("no duplicate repository or authority record exists")
def no_duplicate_records(context) -> None:
    assert len(support.registered_repositories(context.env)) == 1
    assert len(support.registered_authorities(context.env)) == 1


@then("no parent relationship and no dependency relationship are declared")
def no_relationships(context) -> None:
    parents, dependencies = support.relationships(context.env)
    assert parents == []
    assert dependencies == []


@then("no authority beyond the worktree-covering authority exists")
def only_worktree_authority(context) -> None:
    assert len(support.registered_authorities(context.env)) == 1


@then("both invocations report the same session identity and the same session")
def same_session(context) -> None:
    assert context.second == context.session


@then("session establishment succeeds using the worktree-derived identity")
def worktree_derived_identity(context) -> None:
    assert context.session["session"].startswith(context.session["repository"])


@then("that session is distinct from the worktree's default session")
def named_session_distinct(context) -> None:
    assert context.named["space"] != context.session["space"]


@then("neither session displaces the other")
def neither_displaced(context) -> None:
    again = context.env.workspace_json("session", str(context.worktree))
    assert again["space"] == context.session["space"]


@then("one space is held and associated with that repository")
def session_space_held(context) -> None:
    spaces = support.spaces(context.env)
    assert [item["identifier"] for item in spaces] == [context.session["space"]]
    assert spaces[0]["associated_repository_ids"] == [context.session["repository"]]


@then("ZPP reports that space identifier")
def space_reported(context) -> None:
    assert context.session["space"]


@then("the resolved sources include the established session's space-scoped source")
def space_source_resolved(context) -> None:
    bodies = [item["body"] for item in context.resolution["bodies"]]
    assert context.resolution["session"] == context.session["space"]
    assert context.expected_body in bodies


@then("the claim is refused")
def claim_refused(context) -> None:
    assert context.claim.exit_code != 0 or context.closure.exit_code != 0


@then("the refusal names the relationship declaration required")
def refusal_names_relationship(context) -> None:
    output = context.claim.output + getattr(context, "closure", context.claim).output
    assert "relate" in output or "relationship" in output or "dependency" in output


@then(
    "the claim is accepted and the second repository participates in the affected claim"
)
def claim_accepted(context) -> None:
    assert context.claim.exit_code == 0, context.claim.output
    assert context.other_session["repository"] in context.claim.output
