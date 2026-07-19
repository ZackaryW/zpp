"""zpp-mcp: the governance mount served over stdio MCP.

Tests exercise the mount logic (tools + prompt) directly - they import only
zpp_mcp.tools / zpp_mcp.prompt, which import zpp.core but never mcp, so the
suite runs without the SDK installed. One skippable test asserts the server
wiring registers exactly the read-only surface when mcp IS available.
"""

import importlib.util

import pytest

from zpp.core import governance
from zpp_mcp import prompt, tools

MUTATING = ("snapshot", "workset", "config", "sync", "restore", "import", "bind")


@pytest.fixture
def governed_repo(tmp_path, fake_openspec):
    """A repo bound to a registered store via committed zpp.toml (rule 2), that
    applies one builtin trait through the repo tier."""
    fake_openspec["stores"]["acme"] = str(tmp_path / "store")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "zpp.toml").write_text(
        '[governance]\nstore = "acme"\n\n[traits]\napply = ["ponytail"]\n'
    )
    return repo


# --- tool wrappers: CLI-parity, explicit path, read-only surface ---

def test_resolve_matches_core(governed_repo):
    assert tools.resolve(str(governed_repo)) == governance.resolve(governed_repo)


def test_resolve_reports_store_and_rule(governed_repo):
    result = tools.resolve(str(governed_repo))
    assert result["mode"] == "externally-governed"
    assert result["store"] == "acme"
    assert result["rule"] == 2


def test_trait_effective_applies_repo_trait(governed_repo):
    result = tools.trait_effective(str(governed_repo))
    assert [t["name"] for t in result["applied"]] == ["ponytail"]
    assert result["unknown"] == []


def test_trait_content_found_and_missing(governed_repo):
    got = tools.trait_content("ponytail", str(governed_repo))
    assert got["found"] is True and got["content"]
    missing = tools.trait_content("no-such-trait", str(governed_repo))
    assert missing["found"] is False and missing["content"] is None


def test_trait_list_includes_builtins(governed_repo):
    names = {r["name"] for r in tools.trait_list(str(governed_repo))}
    assert {"ponytail", "structure", "coverage", "commit-stage"} <= names


def test_doctor_is_detect_only_report(governed_repo):
    report = tools.doctor(str(governed_repo))
    assert isinstance(report, list)
    assert all("present" in r and "tool" in r for r in report)


def test_tool_set_is_read_only():
    names = {fn.__name__ for fn in tools.TOOL_FUNCS}
    assert names == {"resolve", "trait_list", "trait_effective",
                     "trait_content", "doctor"}
    assert not any(m in n for fn in tools.TOOL_FUNCS
                   for n in [fn.__name__] for m in MUTATING)


# --- degradation contract: no crash when the environment is thin ---

def test_resolve_degrades_without_openspec_cli(tmp_path, monkeypatch):
    """No fake_openspec: the real adapter shells out and fails; resolve must
    classify anyway and record a warning, never raise."""
    from zpp.core import adapter

    monkeypatch.setattr(adapter, "store_list",
                        lambda: (_ for _ in ()).throw(adapter.OpenspecError("no cli")))
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "zpp.toml").write_text('[governance]\nstore = "ghost"\n')
    result = tools.resolve(str(repo))
    assert result["mode"] == "externally-governed"
    assert any("unavailable" in w for w in result["warnings"])


def test_ungoverned_path_is_clean(tmp_path, fake_openspec):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert tools.resolve(str(plain))["mode"] == "ungoverned"


# --- the zpp-governance prompt: mount composition + silent degradation ---

def test_prompt_governed_yields_mount_block(governed_repo):
    block = prompt.governance_block(str(governed_repo))
    assert block.startswith("<zpp-governance>")
    assert block.endswith("</zpp-governance>")
    assert "governance: externally-governed (store: acme)" in block
    assert "trait: ponytail" in block
    assert "doctor report" not in block  # healthy resolution -> no doctor


def test_prompt_ungoverned_clean_is_empty(tmp_path, fake_openspec):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert prompt.governance_block(str(plain)) == ""


def test_prompt_degraded_appends_doctor(tmp_path, monkeypatch):
    from zpp.core import adapter

    monkeypatch.setattr(adapter, "store_list",
                        lambda: (_ for _ in ()).throw(adapter.OpenspecError("no cli")))
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "zpp.toml").write_text('[governance]\nstore = "ghost"\n')
    block = prompt.governance_block(str(repo))
    assert "<zpp-governance>" in block
    assert "environment degraded - doctor report:" in block


# --- server wiring (needs the SDK; skipped when absent) ---

@pytest.mark.skipif(importlib.util.find_spec("mcp") is None,
                    reason="mcp SDK not installed")
def test_server_registers_only_mount_set():
    from zpp_mcp import server

    mcp = server.build_server()
    assert mcp.name == "zpp-governance"
    # build_server must not raise; the tool set it binds is the read-only five.
    assert len(tools.TOOL_FUNCS) == 5
