from pathlib import Path

import pytest

from zpp.utils.models import ManagedStateError
from zpp.utils.skill_bundles import SkillBundle, SkillProjectionInspection
from zpp.utils.skill_lifecycle import (
    differing_managed_versions,
    plan_skill_install,
    plan_skill_remove,
    plan_skill_update,
)


def _bundle() -> SkillBundle:
    return SkillBundle("0.9.0", (), "0" * 64)


def _inspection(
    root: Path,
    state: str,
    *,
    scope: str,
    agents: tuple[str, ...],
    version: str | None = None,
) -> SkillProjectionInspection:
    return SkillProjectionInspection(
        root,
        state,  # type: ignore[arg-type]
        version=version,
        scope=scope,  # type: ignore[arg-type]
        agents=agents,
    )


def test_install_planning_applies_global_dedup_and_force_only_to_absent_local(
    tmp_path: Path,
) -> None:
    selected = (
        _inspection(
            tmp_path / "repo/.agents/skills",
            "absent",
            scope="local",
            agents=("codex", "pi"),
        ),
    )
    global_state = (
        _inspection(
            tmp_path / "home/.agents/skills",
            "compatible",
            scope="global",
            agents=("codex", "pi"),
            version="0.9.0",
        ),
    )

    skipped = plan_skill_install(_bundle(), selected, global_state, force=False)
    forced = plan_skill_install(_bundle(), selected, global_state, force=True)

    assert tuple(action.kind for action in skipped.actions) == ("skip-global",)
    assert tuple(action.kind for action in forced.actions) == ("install",)


def test_install_planning_installs_for_outdated_global_and_replaces_local(
    tmp_path: Path,
) -> None:
    selected = (
        _inspection(
            tmp_path / "repo/.agents/skills",
            "absent",
            scope="local",
            agents=("codex",),
        ),
        _inspection(
            tmp_path / "repo/.claude/skills",
            "outdated",
            scope="local",
            agents=("claude",),
            version="0.8.0",
        ),
    )
    global_state = (
        _inspection(
            tmp_path / "home/.agents/skills",
            "outdated",
            scope="global",
            agents=("codex", "pi"),
            version="0.8.0",
        ),
    )

    plan = plan_skill_install(_bundle(), selected, global_state, force=False)

    assert tuple(action.kind for action in plan.actions) == ("install", "replace")


def test_every_selected_state_is_rejected_before_a_plan_is_returned(
    tmp_path: Path,
) -> None:
    selected = (
        _inspection(
            tmp_path / "first",
            "absent",
            scope="local",
            agents=("pi",),
        ),
        _inspection(
            tmp_path / "conflict",
            "conflict",
            scope="local",
            agents=("claude",),
        ),
    )

    with pytest.raises(ManagedStateError, match="conflict"):
        plan_skill_install(_bundle(), selected, (), force=False)


def test_update_and_remove_plan_only_managed_selected_scopes(tmp_path: Path) -> None:
    selected = (
        _inspection(
            tmp_path / "compatible",
            "compatible",
            scope="global",
            agents=("codex",),
            version="0.9.0",
        ),
        _inspection(
            tmp_path / "outdated",
            "outdated",
            scope="global",
            agents=("claude",),
            version="0.8.0",
        ),
    )

    update = plan_skill_update(_bundle(), selected)
    removal = plan_skill_remove(selected)

    assert tuple(action.kind for action in update.actions) == ("skip-current", "replace")
    assert tuple(action.kind for action in removal.actions) == ("remove", "remove")

    for invalid in ("absent", "conflict"):
        with pytest.raises(ManagedStateError):
            plan_skill_update(
                _bundle(),
                (_inspection(tmp_path / invalid, invalid, scope="global", agents=("pi",)),),
            )
        with pytest.raises(ManagedStateError):
            plan_skill_remove(
                (_inspection(tmp_path / invalid, invalid, scope="global", agents=("pi",)),)
            )


def test_differing_versions_report_without_scope_precedence(tmp_path: Path) -> None:
    inspections = (
        _inspection(
            tmp_path / "global",
            "outdated",
            scope="global",
            agents=("codex", "pi"),
            version="0.8.0",
        ),
        _inspection(
            tmp_path / "local",
            "compatible",
            scope="local",
            agents=("codex",),
            version="0.9.0",
        ),
        _inspection(
            tmp_path / "claude",
            "compatible",
            scope="local",
            agents=("claude",),
            version="0.9.0",
        ),
    )

    differences = differing_managed_versions(inspections)

    assert len(differences) == 1
    assert differences[0].agents == ("codex",)
    assert differences[0].global_version == "0.8.0"
    assert differences[0].local_version == "0.9.0"
    assert not hasattr(differences[0], "preferred_scope")
