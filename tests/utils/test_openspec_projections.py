from pathlib import Path

from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.openspec_projections import (
    inspect_openspec_projection,
    plan_openspec_projection,
)
from zpp.utils.openspec_skills import GeneratedOpenSpecBundle, OPENSPEC_CORE_SKILL_NAMES
from zpp.utils.skill_bundles import SkillFile, fingerprint_skill_files


def _bundle(agent: str, version: str | None, marker: str) -> GeneratedOpenSpecBundle:
    files = tuple(
        SkillFile(f"{name}/SKILL.md", f"{agent}:{marker}:{name}\n".encode())
        for name in OPENSPEC_CORE_SKILL_NAMES
    )
    return GeneratedOpenSpecBundle(
        agent,  # type: ignore[arg-type]
        version,
        files,
        fingerprint_skill_files(files),
    )


def test_projection_install_and_matching_version_preserve_verified_bytes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "skills"
    bundle = _bundle("codex", "1.7.0", "first")

    absent = inspect_openspec_projection(root, "codex", "1.7.0")
    apply_mutation_plan(plan_openspec_projection(root, bundle, absent))
    installed = inspect_openspec_projection(root, "codex", "1.7.0")

    assert absent.state == "absent"
    assert installed.state == "compatible"
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }
    assert plan_openspec_projection(root, _bundle("codex", "1.7.0", "new"), installed).creation.entries == ()
    assert {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    } == before


def test_changed_and_null_versions_replace_only_owned_projection(
    tmp_path: Path,
) -> None:
    root = tmp_path / "skills"
    old = _bundle("claude", None, "old")
    apply_mutation_plan(
        plan_openspec_projection(
            root,
            old,
            inspect_openspec_projection(root, "claude", None),
        )
    )
    unrelated = root / "user-skill" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep", encoding="utf-8")

    outdated = inspect_openspec_projection(root, "claude", "1.8.0")
    current = _bundle("claude", "1.8.0", "new")
    apply_mutation_plan(plan_openspec_projection(root, current, outdated))

    assert outdated.state == "outdated"
    assert inspect_openspec_projection(root, "claude", "1.8.0").state == "compatible"
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_projection_inspection_rejects_unmanaged_and_tampered_core_skills(
    tmp_path: Path,
) -> None:
    unmanaged = tmp_path / "unmanaged"
    collision = unmanaged / OPENSPEC_CORE_SKILL_NAMES[0] / "SKILL.md"
    collision.parent.mkdir(parents=True)
    collision.write_text("user content", encoding="utf-8")
    assert inspect_openspec_projection(unmanaged, "pi", "1.7.0").state == "conflict"

    managed = tmp_path / "managed"
    bundle = _bundle("pi", "1.7.0", "original")
    apply_mutation_plan(
        plan_openspec_projection(
            managed,
            bundle,
            inspect_openspec_projection(managed, "pi", "1.7.0"),
        )
    )
    (managed / OPENSPEC_CORE_SKILL_NAMES[0] / "SKILL.md").write_text(
        "tampered", encoding="utf-8"
    )
    assert inspect_openspec_projection(managed, "pi", "1.7.0").state == "conflict"
