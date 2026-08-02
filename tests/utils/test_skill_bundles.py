from pathlib import Path
import json

import pytest

from zpp.utils.skill_bundles import (
    SKILL_MANIFEST_NAME,
    WORKFLOW_SKILL_NAMES,
    SkillBundle,
    SkillFile,
    collect_skill_bundle,
    fingerprint_skill_files,
    inspect_skill_projection,
    load_skill_manifest,
    manifest_for_bundle,
)
from zpp.utils.models import ManagedStateError


def _valid_bundle_tree(root: Path) -> None:
    for name in WORKFLOW_SKILL_NAMES:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\n---\n\nGuidance π for {name}.\n",
            encoding="utf-8",
        )
    script = root / "zpp-commit-zmem" / "scripts" / "check.bin"
    script.parent.mkdir()
    script.write_bytes(b"\x00\xff\x10")


def test_collect_skill_bundle_preserves_bytes_and_fingerprints_stably(
    tmp_path: Path,
) -> None:
    _valid_bundle_tree(tmp_path)

    first = collect_skill_bundle(tmp_path, "0.9.0")
    second = collect_skill_bundle(tmp_path, "0.9.0")

    assert first.version == "0.9.0"
    assert tuple(file.relative_path for file in first.files) == tuple(
        sorted(file.relative_path for file in first.files)
    )
    assert next(
        file.content
        for file in first.files
        if file.relative_path.endswith("check.bin")
    ) == b"\x00\xff\x10"
    assert first.fingerprint == fingerprint_skill_files(first.files)
    assert first == second


@pytest.mark.parametrize("invalid", ["missing", "unexpected"])
def test_collect_skill_bundle_rejects_invalid_top_level_membership(
    tmp_path: Path,
    invalid: str,
) -> None:
    _valid_bundle_tree(tmp_path)
    if invalid == "missing":
        missing = tmp_path / WORKFLOW_SKILL_NAMES[0]
        for child in missing.iterdir():
            child.unlink()
        missing.rmdir()
    else:
        extra = tmp_path / "zpp-unexpected"
        extra.mkdir()
        (extra / "SKILL.md").write_text("unexpected\n", encoding="utf-8")

    with pytest.raises(ValueError, match="workflow skill bundle"):
        collect_skill_bundle(tmp_path, "0.9.0")


def test_collect_skill_bundle_requires_each_skill_document(tmp_path: Path) -> None:
    _valid_bundle_tree(tmp_path)
    (tmp_path / WORKFLOW_SKILL_NAMES[-1] / "SKILL.md").unlink()

    with pytest.raises(ValueError, match="SKILL.md"):
        collect_skill_bundle(tmp_path, "0.9.0")


def test_collect_skill_bundle_requires_utf8_skill_documents(tmp_path: Path) -> None:
    _valid_bundle_tree(tmp_path)
    (tmp_path / WORKFLOW_SKILL_NAMES[0] / "SKILL.md").write_bytes(b"\xff")

    with pytest.raises(ValueError, match="UTF-8"):
        collect_skill_bundle(tmp_path, "0.9.0")


def _write_projection(root: Path, source: Path, version: str) -> None:
    bundle = collect_skill_bundle(source, version)
    for file in bundle.files:
        destination = root / Path(file.relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file.content)
    manifest = manifest_for_bundle(bundle)
    (root / SKILL_MANIFEST_NAME).write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )


def _write_historical_projection(root: Path) -> None:
    files = tuple(
        SkillFile(
            f"{name}/SKILL.md",
            f"---\nname: {name}\n---\n\nHistorical guidance.\n".encode(),
        )
        for name in WORKFLOW_SKILL_NAMES[:-1]
    )
    bundle = SkillBundle("0.8.0", files, fingerprint_skill_files(files))
    for file in files:
        destination = root / Path(file.relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file.content)
    manifest = manifest_for_bundle(bundle)
    (root / SKILL_MANIFEST_NAME).write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )


def test_inspect_skill_projection_distinguishes_managed_versions(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "skills"
    source.mkdir()
    destination.mkdir()
    _valid_bundle_tree(source)
    expected = collect_skill_bundle(source, "0.9.0")

    assert inspect_skill_projection(destination, expected).state == "absent"

    _write_projection(destination, source, "0.8.0")
    outdated = inspect_skill_projection(destination, expected)
    assert outdated.state == "outdated"
    assert outdated.version == "0.8.0"

    (destination / SKILL_MANIFEST_NAME).write_text(
        json.dumps(manifest_for_bundle(expected).model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )
    compatible = inspect_skill_projection(destination, expected)
    assert compatible.state == "compatible"
    assert compatible.version == "0.9.0"


def test_inspect_skill_projection_accepts_an_intact_historical_inventory(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _valid_bundle_tree(source)
    expected = collect_skill_bundle(source, "0.9.0")
    historical = tmp_path / "historical"
    historical.mkdir()
    _write_historical_projection(historical)

    inspection = inspect_skill_projection(historical, expected)

    assert inspection.state == "outdated"
    assert inspection.version == "0.8.0"


def test_inspect_historical_projection_rejects_unowned_content_in_owned_skill(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _valid_bundle_tree(source)
    expected = collect_skill_bundle(source, "0.9.0")
    historical = tmp_path / "historical"
    historical.mkdir()
    _write_historical_projection(historical)
    (historical / WORKFLOW_SKILL_NAMES[0] / "extra.md").write_text(
        "not declared",
        encoding="utf-8",
    )

    inspection = inspect_skill_projection(historical, expected)

    assert inspection.state == "conflict"
    assert inspection.reason == "managed skill file set differs from its manifest"


def test_inspect_skill_projection_rejects_unmanaged_and_tampered_content(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _valid_bundle_tree(source)
    expected = collect_skill_bundle(source, "0.9.0")

    unmanaged = tmp_path / "unmanaged"
    (unmanaged / WORKFLOW_SKILL_NAMES[0]).mkdir(parents=True)
    assert inspect_skill_projection(unmanaged, expected).state == "conflict"

    managed = tmp_path / "managed"
    managed.mkdir()
    _write_projection(managed, source, "0.9.0")
    (managed / WORKFLOW_SKILL_NAMES[0] / "SKILL.md").write_text(
        "tampered\n",
        encoding="utf-8",
    )
    assert inspect_skill_projection(managed, expected).state == "conflict"


def test_manifest_loading_is_strict_and_rejects_escaping_paths(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert load_skill_manifest(missing) is None

    malformed = tmp_path / "malformed.json"
    malformed.write_bytes(b"\xff")
    with pytest.raises(ManagedStateError, match="manifest"):
        load_skill_manifest(malformed)

    escaping = tmp_path / "escaping.json"
    escaping.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundle_version": "0.9.0",
                "fingerprint": "0" * 64,
                "files": {"../outside": "0" * 64},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ManagedStateError, match="manifest"):
        load_skill_manifest(escaping)


@pytest.mark.parametrize(
    "owned_path",
    ("custom-skill/SKILL.md", "zpp-historical/reference.md"),
)
def test_manifest_loading_requires_zpp_skill_documents(
    tmp_path: Path,
    owned_path: str,
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundle_version": "0.8.0",
                "fingerprint": "0" * 64,
                "files": {owned_path: "0" * 64},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManagedStateError, match="manifest"):
        load_skill_manifest(manifest)
