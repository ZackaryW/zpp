import json
from pathlib import Path

import pytest

from zpp.utils.json_io import atomic_write_json


def test_atomic_write_json_is_valid_and_deterministic(tmp_path: Path) -> None:
    destination = tmp_path / "trait.json"

    atomic_write_json(destination, {"second": 2, "first": 1})
    first_write = destination.read_text(encoding="utf-8")

    atomic_write_json(destination, {"first": 1, "second": 2})
    second_write = destination.read_text(encoding="utf-8")

    assert json.loads(second_write) == {"first": 1, "second": 2}
    assert second_write == first_write


def test_atomic_write_json_preserves_destination_and_cleans_up_on_failure(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "trait.json"
    destination.write_text("original\n", encoding="utf-8")

    with pytest.raises(TypeError):
        atomic_write_json(destination, {"unsupported": object()})

    assert destination.read_text(encoding="utf-8") == "original\n"
    assert list(tmp_path.glob(".trait.json.*.tmp")) == []


def test_atomic_write_json_preserves_unicode_for_utf8_loading(tmp_path: Path) -> None:
    destination = tmp_path / "trait.json"
    value = {"direction": "保留用户写下的方向"}

    atomic_write_json(destination, value)

    with destination.open(encoding="utf-8") as stream:
        loaded = json.load(stream)

    assert loaded == value
    assert "保留用户写下的方向" in destination.read_text(encoding="utf-8")


def test_atomic_write_json_propagates_replace_failure_and_cleans_up(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "trait.json"

    def reject_replace(source: object, target: object) -> None:
        raise PermissionError("replacement denied")

    monkeypatch.setattr("zpp.utils.json_io.os.replace", reject_replace)

    with pytest.raises(PermissionError, match="replacement denied"):
        atomic_write_json(destination, [])

    assert not destination.exists()
    assert list(tmp_path.glob(".trait.json.*.tmp")) == []
