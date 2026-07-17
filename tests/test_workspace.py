import json

from zpp.utils.workspace import _strip_jsonc, load_members


def test_jsonc_comments_and_trailing_commas():
    text = '{\n // comment\n "a": "url//not-comment", /* block */ "b": [1, 2,],\n}'
    assert json.loads(_strip_jsonc(text)) == {"a": "url//not-comment", "b": [1, 2]}


def test_members_resolved_against_file_directory(workspace_file):
    members = load_members(workspace_file)
    assert [m["name"] for m in members] == ["alpha", "repo-b"]
    assert all(m["path"].startswith("/") for m in members)
    assert members[0]["labeled"] and not members[1]["labeled"]
    assert members[0]["path"].endswith("/repo-a")
