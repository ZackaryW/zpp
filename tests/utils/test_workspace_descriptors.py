import json
from pathlib import Path

import pytest

from zpp.utils.workspace_descriptors import load_code_workspace


def test_workspace_loader_preserves_order_labels_relative_paths_and_utf8(
    tmp_path: Path,
) -> None:
    first = tmp_path / "项目一"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    descriptor = tmp_path / "组合.code-workspace"
    descriptor.write_text(
        json.dumps(
            {
                "folders": [
                    {"name": "主要", "path": "项目一"},
                    {"path": "second"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    members = load_code_workspace(descriptor)

    assert [(item.name, item.path) for item in members] == [
        ("主要", first.resolve()),
        ("second", second.resolve()),
    ]


def test_workspace_loader_rejects_invalid_or_missing_members(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.code-workspace"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_code_workspace(invalid)

    missing = tmp_path / "missing.code-workspace"
    missing.write_text('{"folders":[{"path":"absent"}]}', encoding="utf-8")
    with pytest.raises(ValueError, match="existing directory"):
        load_code_workspace(missing)
