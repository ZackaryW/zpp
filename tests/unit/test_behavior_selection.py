import pytest

from zpp.core.behavior import (
    BehaviorAdapterRegistry,
    BehaviorExecutionError,
    BehaviorRunInput,
    parse_behavior_mapping,
    select_behavior_targets,
)
from zpp.utils.behavior_providers import ArgvAdapter


def command():
    raw = {
        "version": 1,
        "commands": {
            "bdd": {
                "provider": {"kind": "argv", "argv": ["run", "{targets}"]},
                "targets": {
                    "core": {
                        "value": "features/core",
                        "paths": ["features/core/**"],
                    },
                    "workflow": {
                        "value": "features/workflow",
                        "paths": ["features/workflow/**"],
                    },
                },
                "gates": {"zpps-workflow-kernel": ["workflow", "core"]},
            }
        },
    }
    return parse_behavior_mapping(
        raw,
        registry=BehaviorAdapterRegistry((ArgvAdapter(),)),
    ).commands["bdd"]


def test_exact_selection_deduplicates_in_declaration_order() -> None:
    selected = select_behavior_targets(
        command(),
        BehaviorRunInput("bdd", targets=("workflow", "core", "workflow")),
    )

    assert tuple(target.name for target in selected) == ("core", "workflow")


def test_gate_and_complete_selection_use_declared_order() -> None:
    gate = select_behavior_targets(
        command(), BehaviorRunInput("bdd", gate="zpps-workflow-kernel")
    )
    complete = select_behavior_targets(
        command(), BehaviorRunInput("bdd", complete=True)
    )

    assert tuple(target.name for target in gate) == ("core", "workflow")
    assert complete == tuple(command().targets.values())


def test_rejects_unknown_or_ambiguous_selection() -> None:
    with pytest.raises(BehaviorExecutionError, match="not declared"):
        select_behavior_targets(
            command(), BehaviorRunInput("bdd", targets=("missing",))
        )
    with pytest.raises(BehaviorExecutionError, match="mutually exclusive"):
        select_behavior_targets(
            command(),
            BehaviorRunInput("bdd", complete=True, gate="zpps-workflow-kernel"),
        )


def test_removed_gate_is_not_translated_and_default_remains_affected() -> None:
    with pytest.raises(BehaviorExecutionError, match="not declared"):
        select_behavior_targets(command(), BehaviorRunInput("bdd", gate="zpp-workflow"))

    selected = select_behavior_targets(
        command(),
        BehaviorRunInput("bdd"),
        changed_paths=("features/workflow/example.feature",),
    )

    assert tuple(target.name for target in selected) == ("workflow",)


def test_default_selection_uses_supplied_changed_paths() -> None:
    selected = select_behavior_targets(
        command(),
        BehaviorRunInput("bdd"),
        changed_paths=("features/workflow/example.feature",),
    )

    assert tuple(target.name for target in selected) == ("workflow",)
