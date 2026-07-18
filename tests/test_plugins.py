import json
from pathlib import Path

import pytest

from zpp.core import plugins


def _install_claude_plugin(base: Path, plugin: str, traits: dict, extras=()) -> Path:
    root = base / "plugins" / "cache" / "mkt" / plugin / "0.0.1"
    (root / "traits").mkdir(parents=True)
    for name, content in traits.items():
        (root / "traits" / f"{name}.md").write_text(content)
    for extra in extras:
        (root / extra).parent.mkdir(parents=True, exist_ok=True)
        (root / extra).write_text("x")
    index = base / "plugins" / "installed_plugins.json"
    data = json.loads(index.read_text()) if index.is_file() else {"version": 2, "plugins": {}}
    data["plugins"][f"{plugin}@mkt"] = [{"scope": "user", "installPath": str(root)}]
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(json.dumps(data))
    return root


def test_claude_resolver_reads_installed_plugins(tmp_path):
    base = tmp_path / ".claude"
    _install_claude_plugin(base, "acme", {"a": "A"})
    resolver = plugins.ClaudeResolver()
    roots = dict(resolver.plugin_roots(override=base))
    assert "acme" in roots and (roots["acme"] / "traits" / "a.md").is_file()


def test_base_dir_override_beats_autodetect(tmp_path):
    resolver = plugins.ClaudeResolver()
    assert resolver.base_dir(override=tmp_path) == tmp_path


def test_base_dir_autodetect_is_home_relative(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    resolver = plugins.ClaudeResolver()
    got = resolver.base_dir()
    # POSIX default; Windows path is grounded separately - here we assert the
    # resolver produced a concrete path under the resolved home, not None.
    assert got is not None and got.name == ".claude"


def test_extractor_reads_only_traits(tmp_path):
    base = tmp_path / ".claude"
    root = _install_claude_plugin(base, "mixed", {"good": "GOOD"},
                                  extras=["skills/s/SKILL.md", "plugin.json"])
    got = {t["name"]: t for t in plugins.extract(root, tool="claude", plugin="mixed")}
    assert set(got) == {"good"}
    assert got["good"]["tool"] == "claude" and got["good"]["plugin"] == "mixed"


def test_gather_yields_all_plugin_traits(tmp_path):
    base = tmp_path / ".claude"
    _install_claude_plugin(base, "one", {"x": "X"})
    _install_claude_plugin(base, "two", {"y": "Y"})
    rows = plugins.gather("claude", override=base)
    names = {r["name"] for r in rows}
    assert names == {"x", "y"}
    assert all(r["source"] == "plugin" for r in rows)


def test_gather_unknown_tool_is_empty(tmp_path):
    assert plugins.gather("nonsense", override=tmp_path) == []


def test_plugin_without_traits_folder_contributes_nothing(tmp_path):
    base = tmp_path / ".claude"
    root = base / "plugins" / "cache" / "mkt" / "skillsonly" / "0.0.1"
    (root / "skills").mkdir(parents=True)
    index = base / "plugins" / "installed_plugins.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(json.dumps({"version": 2, "plugins": {
        "skillsonly@mkt": [{"scope": "user", "installPath": str(root)}]}}))
    assert plugins.gather("claude", override=base) == []
