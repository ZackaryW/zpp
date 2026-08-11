from __future__ import annotations

from pathlib import Path

import zpp.artifacts
from zpp.artifacts import (
    packaged_trait_source,
    packaged_traits,
    packaged_workflow_skill,
)
from zpp.core.models import SourceKind


def test_packaged_assets_are_loaded_before_resource_lifetime_ends(
    tmp_path: Path,
    monkeypatch,
) -> None:
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "z.toml").write_bytes(b"z-content")
    (traits / "a.toml").write_bytes(b"a-content")
    skill = tmp_path / "skills" / "zpp-workflow"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: zpp-workflow\ndescription: Run the ZPP workflow.\n---\nRun it.\n"
    )
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    loaded_skill = packaged_workflow_skill()
    loaded_traits = packaged_traits()

    assert loaded_skill.name == "zpp-workflow"
    assert [item.family for item in loaded_traits] == ["a", "z"]
    assert [item.content for item in loaded_traits] == [
        b"a-content",
        b"z-content",
    ]


def test_packaged_toml_becomes_a_detached_global_bound_source(
    tmp_path: Path,
    monkeypatch,
) -> None:
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "bdd.toml").write_text(
        "[meta]\nselection = 'first-win'\n"
        "[[trait]]\n[trait.content]\nbody = 'packaged bdd'\n"
    )
    monkeypatch.setattr(zpp.artifacts, "files", lambda _package: tmp_path)

    source = packaged_trait_source()

    assert source.kind is SourceKind.GLOBAL
    assert source.identifier == "zpp:packaged"
    assert [item.family for item in source.documents] == ["bdd"]
    assert source.documents[0].values["meta"] == {"selection": "first-win"}
