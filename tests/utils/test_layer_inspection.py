from pathlib import Path

from zpp.utils.layer_inspection import inspect_authored_layer
from zpp.utils.layouts import authored_layer_paths


def test_layer_inspection_reports_complete_and_aggregated_invalid_state(
    tmp_path: Path,
) -> None:
    complete_paths = authored_layer_paths(tmp_path / "complete")
    complete_paths.traits.mkdir(parents=True)
    complete_paths.config.write_text("{}\n", encoding="utf-8")
    complete_paths.triggers.write_text("[]\n", encoding="utf-8")
    (complete_paths.traits / "valid.md").write_text(
        "---\nname: valid\ndescription: Valid\n---\nBody\n",
        encoding="utf-8",
    )

    invalid_paths = authored_layer_paths(tmp_path / "invalid")
    invalid_paths.traits.mkdir(parents=True)
    invalid_paths.config.write_text("not-json", encoding="utf-8")
    invalid_paths.triggers.write_text("{}\n", encoding="utf-8")
    (invalid_paths.traits / "one.md").write_text("invalid", encoding="utf-8")
    (invalid_paths.traits / "two.md").write_text(
        "---\nname: wrong\n---\n",
        encoding="utf-8",
    )

    complete = inspect_authored_layer(complete_paths)
    invalid = inspect_authored_layer(invalid_paths)

    assert complete.state == "complete"
    assert complete.missing == () and complete.issues == ()
    assert invalid.state == "invalid"
    assert {issue.source for issue in invalid.issues} >= {
        invalid_paths.config,
        invalid_paths.triggers,
        invalid_paths.traits / "one.md",
        invalid_paths.traits / "two.md",
    }
