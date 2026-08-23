from __future__ import annotations

import json
from uuid import uuid4

import support
from behave import given, then, when


def _environment(context) -> support.Environment:
    environment = support.Environment()
    context.environment = environment
    return environment


@given(
    "a monorepo with repository traits and parent child and sibling "
    "zpp-traits namespaces"
)
def monorepo_traits(context) -> None:
    _environment(context).add_repository_trait()


@when("ZPP resolves traits for the selected child through its public interface")
def resolve_child(context) -> None:
    context.result = context.environment.invoke_json(
        "resolve",
        str(context.environment.child),
        "--trait",
        "bundle-policy",
        "--explain",
    )


@then("repository parent and selected-child inputs are composed in order")
def composed_order(context) -> None:
    assert [item["body"] for item in context.result["bodies"]] == [
        "repository",
        "parent",
        "child",
    ]


@then("the sibling input and lease state are absent")
def sibling_and_state_absent(context) -> None:
    assert "sibling" not in json.dumps(context.result)
    assert not context.environment.home.exists()


@given("an automatic workflow with exact store and change members")
def exact_members(context) -> None:
    _environment(context)
    context.members = ((support.PARENT, "platform-change"),)


@when("the workflow begins governed mutation through the minimal lease bridge")
def acquire_before_mutation(context) -> None:
    context.acquisition = context.environment.acquire(*context.members)


@then(
    "one Bundler bundle holds the declared roots and descendant closure before mutation"
)
def bundle_closure(context) -> None:
    bundle = context.acquisition["bundle"]
    assert bundle["requested_roots"] == [str(support.PARENT)]
    assert bundle["held_stores"] == sorted(
        str(value) for value in (support.PARENT, support.CHILD, support.SIBLING)
    )


@then("no session claim permit or dependency edge is created")
def only_bundle_state(context) -> None:
    bundles = context.environment.status()["bundles"]
    assert len(bundles) == 1
    assert set(bundles[0]) == {
        "bundle_uuid",
        "owner_id",
        "requested_roots",
        "held_stores",
        "members",
        "archived_members",
        "topology_digest",
    }


@given("a fresh ZPP home and an unprepared registered OpenSpec store")
def unprepared_registered_store(context) -> None:
    _environment(context).use_unprepared_store()


@given("a prepared store and a strict workflow owner override")
def prepared_store_with_owner_override(context) -> None:
    environment = _environment(context)
    context.override_owner = f"workflow:{uuid4()}"
    context.coordination_environment = {
        "ZPP_WORKFLOW_COORDINATION": json.dumps(
            {"version": 1, "owner_id": context.override_owner},
            separators=(",", ":"),
            sort_keys=True,
        )
    }
    context.coordination_root = environment.child


@when("the runtime coordinates the exact store and change without internal identifiers")
def automatic_runtime_coordination(context) -> None:
    environment = context.environment
    root = getattr(context, "coordination_root", environment.unprepared)
    context.acquisition = environment.acquire_target(
        root,
        "runtime-change",
        environment=getattr(context, "coordination_environment", None),
    )


@then("the store and selected ZPP home gain stable coordination identities")
def coordination_identities_created(context) -> None:
    assert (context.environment.unprepared / "openspec" / "bundler.toml").is_file()
    assert (context.environment.home / "identity.json").is_file()


@then("one exact Bundler bundle is acquired under the managed owner")
def exact_managed_bundle(context) -> None:
    bundle = context.acquisition["bundle"]
    assert bundle["owner_id"].startswith("zpp:")
    assert [item["change_name"] for item in bundle["members"]] == ["runtime-change"]


@then("the exact bundle uses the overridden owner")
def overridden_owner_used(context) -> None:
    assert context.acquisition["bundle"]["owner_id"] == context.override_owner


@then("coordination remains leased rather than bypassed")
def override_remains_leased(context) -> None:
    assert context.acquisition["coordination"] == "leased"
    assert context.environment.status()["bundles"]


@given("an automatic workflow bundle with two store and change members")
def two_member_bundle(context) -> None:
    _environment(context)
    context.members = (
        (support.CHILD, "api-change"),
        (support.SIBLING, "web-change"),
    )
    context.bundle = context.environment.acquire(*context.members)["bundle"][
        "bundle_uuid"
    ]


@when("the workflow records only one member archive")
def first_archive(context) -> None:
    context.environment.archive(context.bundle, context.members[0])


@then("the complete bundle remains held")
def bundle_retained(context) -> None:
    bundles = context.environment.status()["bundles"]
    assert [item["bundle_uuid"] for item in bundles] == [context.bundle]


@when("the workflow records the remaining archive and completes the bundle")
def remaining_archive(context) -> None:
    context.environment.archive(context.bundle, context.members[1])
    context.environment.complete(context.bundle)


@then("the complete bundle is released")
def bundle_released(context) -> None:
    assert context.environment.status()["bundles"] == []


@given("the installed ZPP command hook and packaged-skill inventories")
def inventories(context) -> None:
    context.inventory = _environment(context).public_inventory()


@when("their public identities are inspected")
def inspect_identities(context) -> None:
    assert context.inventory


@then("the minimal lease bridge and zpp-traits hook are present")
def current_identities(context) -> None:
    assert "lease" in context.inventory["help"]
    assert context.inventory["hook"] == "zpp-traits"


@then(
    "workspace sessions permits dependencies successors and compatibility "
    "aliases are absent"
)
def retired_identities(context) -> None:
    assert "workspace" not in context.inventory["help"]
    assert "zpp-workspace-management" not in context.inventory["skills"]


@given("a selected ZPP home containing legacy OpenLease state")
def legacy_state(context) -> None:
    environment = _environment(context)
    context.legacy = environment.home / "openlease" / "marker"
    context.legacy.parent.mkdir(parents=True)
    context.legacy.write_text("preserve", encoding="utf-8")


@when("an automatic workflow acquires its first store bundle")
def first_bundle(context) -> None:
    context.environment.acquire((support.CHILD, "api-change"))


@then("only the selected home's bundler child gains lease state")
def bundler_boundary(context) -> None:
    assert (context.environment.home / "bundler" / "state.json").is_file()


@then("the legacy state remains unchanged")
def legacy_unchanged(context) -> None:
    assert context.legacy.read_text(encoding="utf-8") == "preserve"
