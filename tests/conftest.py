import json

import pytest

from zpp.core import adapter


@pytest.fixture(autouse=True)
def zpp_home(tmp_path, monkeypatch):
    home = tmp_path / "zpp-home"
    monkeypatch.setenv("ZPP_HOME", str(home))
    return home


@pytest.fixture
def fake_openspec(monkeypatch):
    """In-memory stand-in for the openspec CLI behind the adapter."""
    state = {"worksets": {}, "stores": {}}
    monkeypatch.setattr(adapter, "workset_list", lambda: dict(state["worksets"]))
    monkeypatch.setattr(
        adapter, "workset_create",
        lambda name, members: state["worksets"].__setitem__(name, members),
    )
    monkeypatch.setattr(
        adapter, "workset_remove", lambda name: state["worksets"].pop(name)
    )
    monkeypatch.setattr(adapter, "workset_open", lambda name, tool=None: None)
    monkeypatch.setattr(adapter, "store_list", lambda: dict(state["stores"]))
    return state


@pytest.fixture
def workspace_file(tmp_path):
    """A .code-workspace with two real member folders, one labeled."""
    (tmp_path / "repo-a").mkdir()
    (tmp_path / "repo-b").mkdir()
    file = tmp_path / "demo.code-workspace"
    file.write_text(json.dumps({
        "folders": [
            {"name": "alpha", "path": "repo-a"},
            {"path": "repo-b"},
        ]
    }))
    return file
