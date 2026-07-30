from pathlib import Path

import pytest

from zpp.utils.models import LayerControls, TriggerRule
from zpp.utils.triggers import (
    activated_trait_names,
    compose_trigger_rules,
    workspace_contains_any,
)


def test_trigger_composition_replaces_then_activates_once_in_first_match_order(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("", encoding="utf-8")
    layers = (
        LayerControls(
            triggers=(TriggerRule(trait="discarded"), TriggerRule(trait="alpha")),
        ),
        LayerControls(trait_overwrites=True),
        LayerControls(
            triggers=(
                TriggerRule(trait="alpha"),
                TriggerRule(trait="workspace", workspace_contain=("src/**/*.py",)),
                TriggerRule(trait="alpha", which="tool"),
                TriggerRule(trait="missing", which="missing"),
            )
        ),
    )
    monkeypatch.setattr(
        "zpp.utils.triggers.shutil.which",
        lambda name: "C:/bin/tool" if name == "tool" else None,
    )

    rules = compose_trigger_rules(layers)

    assert activated_trait_names(rules, target=tmp_path) == ("alpha", "workspace")


def test_workspace_trigger_propagates_traversal_errors(
    tmp_path: Path,
    monkeypatch,
) -> None:
    denied = tmp_path / "denied"
    denied.mkdir()
    original_scandir = __import__("os").scandir

    def denied_scandir(path):
        if Path(path) == denied:
            raise PermissionError(denied)
        return original_scandir(path)

    monkeypatch.setattr("zpp.utils.triggers.os.scandir", denied_scandir)

    with pytest.raises(PermissionError):
        workspace_contains_any(tmp_path, ("**/*.py",))
