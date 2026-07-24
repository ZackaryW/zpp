import json

from typer.testing import CliRunner

from zpp.cli import app


runner = CliRunner()


def test_lease_cli_acquire_status_release(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()

    acquired = runner.invoke(
        app,
        ["lease", "acquire", str(root), "main", "--mode", "write",
         "--session", "agent-one", "--json"],
    )
    status = runner.invoke(
        app, ["lease", "status", str(root), "main", "--json"]
    )
    released = runner.invoke(
        app, ["lease", "release", str(root), "main", "--session", "agent-one", "--json"]
    )

    assert acquired.exit_code == status.exit_code == released.exit_code == 0
    assert json.loads(acquired.stdout)["holder"]["mode"] == "write"
    assert json.loads(status.stdout)["state"] == "live"
    assert json.loads(released.stdout)["released"] is True


def test_lease_cli_conflict_is_nonzero_and_names_holder(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()
    runner.invoke(
        app,
        ["lease", "acquire", str(root), "main", "--mode", "write",
         "--session", "agent-one"],
    )

    conflict = runner.invoke(
        app,
        ["lease", "acquire", str(root), "main", "--mode", "write",
         "--session", "agent-two"],
    )

    assert conflict.exit_code == 1
    assert "agent-one" in conflict.stderr
