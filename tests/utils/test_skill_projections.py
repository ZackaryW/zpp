from pathlib import Path

import pytest

from zpp.utils.skill_bundles import WORKFLOW_SKILL_NAMES, collect_skill_bundle
from zpp.utils.skill_projections import (
    inspect_skill_scopes,
    openspec_projection_roots,
    skill_projection_roots,
)


def _bundle(root: Path):
    for name in WORKFLOW_SKILL_NAMES:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(name, encoding="utf-8")
    return collect_skill_bundle(root, "0.9.0")


def test_skill_projection_roots_keep_pi_native_and_agent_families_independent(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    target = tmp_path / "repo" / "nested"

    local = skill_projection_roots(
        home=home,
        target=target,
        scope="local",
        agents=("claude", "pi", "codex", "pi"),
    )

    assert tuple(item.root for item in local) == (
        target / ".claude" / "skills",
        target / ".pi" / "skills",
        target / ".agents" / "skills",
    )
    assert local[0].agents == ("claude",)
    assert local[1].agents == ("pi",)
    assert local[2].agents == ("codex",)
    assert all(".zpp" not in item.root.parts for item in local)

    global_roots = skill_projection_roots(
        home=home,
        target=None,
        scope="global",
        agents=("codex", "claude", "pi"),
    )
    assert tuple(item.root for item in global_roots) == (
        home / ".agents" / "skills",
        home / ".claude" / "skills",
        home / ".pi" / "agent" / "skills",
    )
    assert tuple(item.agents for item in global_roots) == (
        ("codex",),
        ("claude",),
        ("pi",),
    )

    openspec = openspec_projection_roots(
        home=home,
        target=target,
        scope="local",
        agents=("codex", "pi", "claude"),
    )
    assert tuple(item.root for item in openspec) == (
        target / ".codex" / "skills",
        target / ".pi" / "skills",
        target / ".claude" / "skills",
    )


def test_skill_projection_roots_require_scope_appropriate_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="local"):
        skill_projection_roots(
            home=tmp_path,
            target=None,
            scope="local",
            agents=("codex",),
        )
    with pytest.raises(ValueError, match="global"):
        skill_projection_roots(
            home=tmp_path,
            target=tmp_path / "repo",
            scope="global",
            agents=("codex",),
        )


def test_inspect_skill_scopes_preserves_coalesced_projection_order(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    bundle = _bundle(source)
    projections = skill_projection_roots(
        home=tmp_path / "home",
        target=tmp_path / "repo",
        scope="local",
        agents=("claude", "codex", "pi"),
    )

    inspections = inspect_skill_scopes(projections, bundle)

    assert tuple(item.root for item in inspections) == tuple(
        projection.root for projection in projections
    )
    assert tuple(item.state for item in inspections) == (
        "absent",
        "absent",
        "absent",
    )
