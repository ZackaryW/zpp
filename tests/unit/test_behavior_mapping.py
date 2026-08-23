from collections.abc import Mapping
from copy import deepcopy

import pytest

from zpp.core.behavior import (
    BehaviorAdapterRegistry,
    BehaviorMappingError,
    parse_behavior_mapping,
    select_affected_targets,
)
from zpp.utils.behavior_providers import ArgvAdapter


def mapping() -> Mapping[str, object]:
    return {
        "version": 1,
        "commands": {
            "bdd": {
                "provider": {
                    "kind": "argv",
                    "argv": ["uv", "run", "behave", "{targets}"],
                },
                "targets": {
                    "core": {
                        "value": "features/core",
                        "paths": ["features/core/**", "src/zpp/core/**"],
                    },
                    "workflow": {
                        "value": "features/workflow",
                        "paths": ["features/workflow/**"],
                    },
                },
            }
        },
    }


def registry() -> BehaviorAdapterRegistry:
    return BehaviorAdapterRegistry((ArgvAdapter(),))


def test_parses_mapping_and_preserves_declaration_order() -> None:
    parsed = parse_behavior_mapping(mapping(), registry=registry())

    assert tuple(parsed.commands) == ("bdd",)
    assert tuple(parsed.commands["bdd"].targets) == ("core", "workflow")
    assert parsed.commands["bdd"].provider.kind == "argv"


def test_parses_gate_targets_in_target_declaration_order() -> None:
    raw = deepcopy(mapping())
    raw["commands"]["bdd"]["gates"] = {  # type: ignore[index]
        "zpps-workflow-kernel": ["workflow", "core"]
    }

    parsed = parse_behavior_mapping(raw, registry=registry())

    assert parsed.commands["bdd"].gates == {
        "zpps-workflow-kernel": ("core", "workflow")
    }


@pytest.mark.parametrize(
    "mutation",
    [
        {"version": 2},
        {"extra": True},
        {
            "commands": {
                "bdd": {
                    "provider": {"kind": "argv", "argv": ["x", "{targets}"]},
                    "targets": {
                        "a": {"value": "same", "paths": ["a/**"]},
                        "b": {"value": "same", "paths": ["b/**"]},
                    },
                }
            }
        },
    ],
)
def test_rejects_closed_invalid_mapping(mutation: Mapping[str, object]) -> None:
    raw = dict(mapping())
    raw.update(mutation)

    with pytest.raises(BehaviorMappingError):
        parse_behavior_mapping(raw, registry=registry())


def test_affected_selection_unions_matches_in_declared_order() -> None:
    command = parse_behavior_mapping(mapping(), registry=registry()).commands["bdd"]

    selected = select_affected_targets(
        command,
        ("features/workflow/test.feature", "src/zpp/core/state.py"),
    )

    assert tuple(target.value for target in selected) == (
        "features/core",
        "features/workflow",
    )


def test_affected_selection_falls_back_to_all_for_unknown_path() -> None:
    command = parse_behavior_mapping(mapping(), registry=registry()).commands["bdd"]

    assert select_affected_targets(command, ("README.md",)) == tuple(
        command.targets.values()
    )
    assert select_affected_targets(command, ()) == ()
