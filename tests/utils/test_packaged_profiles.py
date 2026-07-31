import json
from pathlib import Path

import pytest

from zpp.utils.packaged_profiles import load_packaged_default_profile
from zpp.utils.models import ZppValidationError


BASE_TRAITS = ("automatic-workflow", "zero-assumptions", "ponytail")
PYTHON_TRAITS = ("python-bdd", "python-tdd", "python-build")


def test_load_packaged_default_profile_uses_validated_resource_snapshot(
    tmp_path: Path,
    monkeypatch,
) -> None:
    artifacts = tmp_path / "artifacts"
    profile = artifacts / "profiles" / "default"
    traits = profile / "traits"
    traits.mkdir(parents=True)
    (profile / "config.json").write_text(
        '{ "trait_overwrites": false, "traitsConfig": {} }\n',
        encoding="utf-8",
    )
    (profile / "trait.json").write_text(
        "["
        + ",".join(f'{{"trait":"{name}"}}' for name in BASE_TRAITS)
        + "]\n",
        encoding="utf-8",
    )
    for name in BASE_TRAITS + PYTHON_TRAITS:
        (traits / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: {name}\n---\n{name}\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(
        "zpp.utils.packaged_profiles.files",
        lambda package: artifacts,
    )

    snapshot = load_packaged_default_profile()

    assert {item.relative_path.as_posix() for item in snapshot.files} == {
        "config.json",
        "trait.json",
        *(f"traits/{name}.md" for name in BASE_TRAITS + PYTHON_TRAITS),
    }
    trigger_source = next(
        item.content
        for item in snapshot.files
        if item.relative_path.as_posix() == "trait.json"
    )
    assert json.loads(trigger_source) == [
        {"trait": name}
        for name in BASE_TRAITS
    ]


def test_load_packaged_default_profile_rejects_a_malformed_resource(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts = tmp_path / "artifacts"
    profile = artifacts / "profiles" / "default"
    traits = profile / "traits"
    traits.mkdir(parents=True)
    (profile / "config.json").write_text(
        '{"trait_overwrites": false, "traitsConfig": {}}\n',
        encoding="utf-8",
    )
    (profile / "trait.json").write_text(
        '[{"trait":"automatic-workflow"}]\n',
        encoding="utf-8",
    )
    (traits / "automatic-workflow.md").write_text(
        "---\nname: wrong\ndescription: Wrong\n---\nBody\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "zpp.utils.packaged_profiles.files",
        lambda package: artifacts,
    )

    with pytest.raises(ZppValidationError):
        load_packaged_default_profile()
