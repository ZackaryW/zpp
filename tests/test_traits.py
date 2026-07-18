from pathlib import Path

from zpp.core import traits


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_precedence_user_over_builtin_over_saucepan(zpp_home):
    _write(zpp_home / "user" / "ponytail.md", "user copy\n")
    _write(zpp_home / "saucepan" / "acme" / "ponytail.md", "remote copy\n")
    available = traits.available()
    winner = [t for t in available if t["name"] == "ponytail" and not t["shadowed"]]
    assert len(winner) == 1 and winner[0]["source"] == "user"
    shadowed_sources = {t["source"] for t in available
                       if t["name"] == "ponytail" and t["shadowed"]}
    assert shadowed_sources == {"builtin", "saucepan"}


def test_builtin_discipline_set_ships(zpp_home):
    names = {t["name"] for t in traits.available() if t["source"] == "builtin"}
    assert {"ponytail", "structure", "coverage", "commit-stage"} <= names


def test_pack_version_surfaces(zpp_home):
    _write(zpp_home / "saucepan" / "acme" / "acme-style.md")
    _write(zpp_home / "saucepan" / "acme" / "sauce.json",
           '{"name": "acme", "version": "1.2.0", "description": "d"}')
    row = next(t for t in traits.available() if t["name"] == "acme-style")
    assert row["source"] == "saucepan" and row["version"] == "1.2.0"


def test_content_reads_winning_source(zpp_home):
    _write(zpp_home / "user" / "structure.md", "user structure\n")
    assert traits.content("structure") == "user structure\n"
    assert traits.content("nope") is None


def test_effective_attributes_introducing_tier(zpp_home, tmp_path):
    repo = tmp_path / "selfgov"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.default.toml").write_text('[traits]\napply = ["ponytail"]\n')
    (repo / "zpp.toml").write_text('[traits]\napply = ["structure"]\n')
    result = traits.effective(repo)
    tiers = {item["name"]: item["tier"] for item in result["applied"]}
    assert tiers == {"ponytail": "store", "structure": "repo"}


def test_four_source_precedence_and_plugin_tier(zpp_home, tmp_path, monkeypatch):
    # plugin outranks saucepan but not builtin; later plugin wins within tier
    (zpp_home / "saucepan" / "rem").mkdir(parents=True)
    (zpp_home / "saucepan" / "rem" / "shared.md").write_text("REMOTE\n")

    def fake_gather(tool, override=None):
        return [
            {"name": "shared", "source": "plugin", "path": str(tmp_path / "p1.md"),
             "version": None, "tool": tool, "plugin": "p1"},
            {"name": "shared", "source": "plugin", "path": str(tmp_path / "p2.md"),
             "version": None, "tool": tool, "plugin": "p2"},
            {"name": "ponytail", "source": "plugin", "path": str(tmp_path / "pp.md"),
             "version": None, "tool": tool, "plugin": "hijack"},
        ]
    (tmp_path / "p1.md").write_text("P1\n")
    (tmp_path / "p2.md").write_text("P2\n")
    (tmp_path / "pp.md").write_text("HIJACK\n")
    monkeypatch.setattr(traits.plugins, "gather", fake_gather)

    rows = traits.available(tool="claude")
    winner = {r["name"]: r for r in rows if not r["shadowed"]}
    assert winner["shared"]["source"] == "plugin"         # plugin > saucepan
    assert winner["shared"]["plugin"] == "p2"             # later plugin wins tier
    assert winner["ponytail"]["source"] == "builtin"      # builtin unshadowable
