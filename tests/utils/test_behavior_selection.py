from __future__ import annotations

import pytest

from zpp.utils.behavior_mapping import ArgvProvider, BehaviorCommand, BehaviorTarget
from zpp.utils.behavior_selection import expand_target_argv, select_affected_targets


def command() -> BehaviorCommand:
    return BehaviorCommand(
        provider=ArgvProvider(argv=("runner", "{targets}", "--quiet")),
        targets={
            "core": BehaviorTarget(
                value="features/core", paths=("features/core/**", "src/zpp/core/**")
            ),
            "workflow": BehaviorTarget(
                value="features/workflow", paths=("features/workflow/**", "src/zpp/utils/skill_*.py")
            ),
            "codespaces": BehaviorTarget(
                value="features/codespaces",
                paths=("features/codespaces/**", "src/zpp/utils/codespace_*.py"),
            ),
        },
    )


def test_selection_unions_matches_in_declared_order() -> None:
    selected = select_affected_targets(
        command(),
        ("src/zpp/utils/codespace_state.py", "features/core/bootstrap.feature"),
    )

    assert tuple(target.value for target in selected) == (
        "features/core",
        "features/codespaces",
    )


def test_one_unknown_path_conservatively_selects_every_target() -> None:
    selected = select_affected_targets(
        command(), ("features/core/bootstrap.feature", "README.md")
    )

    assert selected == tuple(command().targets.values())


def test_clean_change_selects_nothing() -> None:
    assert select_affected_targets(command(), ()) == ()


def test_expand_target_argv_inserts_distinct_values_without_interpolation() -> None:
    assert expand_target_argv(
        ("runner", "--before", "{targets}", "--after"),
        ("first target", "$(unsafe);still-one-argument"),
    ) == (
        "runner",
        "--before",
        "first target",
        "$(unsafe);still-one-argument",
        "--after",
    )


@pytest.mark.parametrize(
    "argv", [("runner",), ("runner", "{targets}", "{targets}")]
)
def test_expand_target_argv_rejects_an_invalid_marker_count(
    argv: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        expand_target_argv(argv, ("target",))
