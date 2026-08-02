from pathlib import Path

import pytest

from zpp.utils.skill_bundles import (
    SKILL_MANIFEST_NAME,
    WORKFLOW_SKILL_NAMES,
    SkillBundle,
    SkillFile,
    collect_skill_bundle,
    fingerprint_skill_files,
    inspect_skill_projection,
)
from zpp.utils.skill_lifecycle import (
    apply_skill_lifecycle,
    plan_skill_install,
    plan_skill_remove,
    plan_skill_update,
)
from zpp.utils.skill_projections import inspect_skill_scopes, skill_projection_roots


def _bundle(root: Path, version: str, marker: str):
    for name in WORKFLOW_SKILL_NAMES:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\n---\n\n{marker} π\n",
            encoding="utf-8",
        )
    script = root / "zpp-commit-zmem" / "scripts" / "check.bin"
    script.parent.mkdir()
    script.write_bytes(b"\x00\xff" + marker.encode("utf-8"))
    return collect_skill_bundle(root, version)


def _historical_bundle(version: str, marker: str) -> SkillBundle:
    files = tuple(
        SkillFile(
            f"{name}/SKILL.md",
            f"---\nname: {name}\n---\n\n{marker} π\n".encode("utf-8"),
        )
        for name in WORKFLOW_SKILL_NAMES[:-1]
    )
    return SkillBundle(version, files, fingerprint_skill_files(files))


def test_apply_skill_lifecycle_installs_exact_bytes_across_projections(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    bundle = _bundle(source, "0.9.0", "current")
    projections = skill_projection_roots(
        home=tmp_path / "home",
        target=tmp_path / "repo",
        scope="local",
        agents=("codex", "claude"),
    )
    for projection in projections:
        projection.root.mkdir(parents=True)
        (projection.root / "unrelated.md").write_text("keep", encoding="utf-8")
    selected = inspect_skill_scopes(projections, bundle)
    plan = plan_skill_install(bundle, selected, (), force=False)

    apply_skill_lifecycle(bundle, plan)

    for projection in projections:
        assert inspect_skill_projection(projection.root, bundle).state == "compatible"
        assert (projection.root / "unrelated.md").read_text(encoding="utf-8") == "keep"
        assert (
            projection.root / "zpp-commit-zmem" / "scripts" / "check.bin"
        ).read_bytes() == b"\x00\xffcurrent"


def test_apply_skill_lifecycle_replaces_and_removes_only_managed_paths(
    tmp_path: Path,
) -> None:
    old_source = tmp_path / "old"
    current_source = tmp_path / "current"
    old_source.mkdir()
    current_source.mkdir()
    old = _bundle(old_source, "0.8.0", "old")
    current = _bundle(current_source, "0.9.0", "current")
    projections = skill_projection_roots(
        home=tmp_path / "home",
        target=tmp_path / "repo",
        scope="local",
        agents=("pi",),
    )
    root = projections[0].root
    root.mkdir(parents=True)
    unrelated = root / "third-party" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep", encoding="utf-8")

    old_plan = plan_skill_install(old, inspect_skill_scopes(projections, old), (), force=False)
    apply_skill_lifecycle(old, old_plan)
    replacement = plan_skill_install(
        current,
        inspect_skill_scopes(projections, current),
        (),
        force=False,
    )
    apply_skill_lifecycle(current, replacement)

    assert inspect_skill_projection(root, current).state == "compatible"
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_apply_skill_lifecycle_updates_a_historical_owned_inventory(
    tmp_path: Path,
) -> None:
    current_source = tmp_path / "current"
    current_source.mkdir()
    historical = _historical_bundle("0.8.0", "historical")
    current = _bundle(current_source, "0.9.0", "current")
    projections = skill_projection_roots(
        home=tmp_path / "home",
        target=None,
        scope="global",
        agents=("codex",),
    )
    root = projections[0].root
    root.mkdir(parents=True)
    unrelated = root / "third-party" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep", encoding="utf-8")
    install = plan_skill_install(
        historical,
        inspect_skill_scopes(projections, historical),
        (),
        force=False,
    )
    apply_skill_lifecycle(historical, install)

    inspection = inspect_skill_scopes(projections, current)
    assert inspection[0].state == "outdated"
    update = plan_skill_update(current, inspection)
    apply_skill_lifecycle(current, update)

    assert inspect_skill_projection(root, current).state == "compatible"
    assert (root / WORKFLOW_SKILL_NAMES[-1] / "SKILL.md").is_file()
    assert unrelated.read_text(encoding="utf-8") == "keep"

    removal = plan_skill_remove(inspect_skill_scopes(projections, current))
    apply_skill_lifecycle(current, removal)

    assert not (root / SKILL_MANIFEST_NAME).exists()
    assert all(not (root / name).exists() for name in WORKFLOW_SKILL_NAMES)
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_apply_skill_lifecycle_rolls_back_every_projection_on_late_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    bundle = _bundle(source, "0.9.0", "current")
    projections = skill_projection_roots(
        home=tmp_path / "home",
        target=tmp_path / "repo",
        scope="local",
        agents=("codex", "claude"),
    )
    plan = plan_skill_install(
        bundle,
        inspect_skill_scopes(projections, bundle),
        (),
        force=False,
    )
    from zpp.utils import state_mutation

    real_write = state_mutation.atomic_write_bytes
    late_root = projections[-1].root

    def fail_late(destination: Path, source_bytes: bytes) -> None:
        if late_root in destination.parents:
            raise PermissionError("blocked late projection")
        real_write(destination, source_bytes)

    monkeypatch.setattr(state_mutation, "atomic_write_bytes", fail_late)

    with pytest.raises(PermissionError, match="blocked late projection"):
        apply_skill_lifecycle(bundle, plan)

    for projection in projections:
        assert not (projection.root / SKILL_MANIFEST_NAME).exists()
        assert all(not (projection.root / name).exists() for name in WORKFLOW_SKILL_NAMES)
