import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from zpp.cli import app

runner = CliRunner()


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


@pytest.fixture
def environment(tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "--quiet", "-m", "base")
    return home, root


def _run(home: Path, *arguments: str):
    return runner.invoke(app, ["--path", str(home), "workspace", *arguments])


def _json(home: Path, *arguments: str):
    result = _run(home, *arguments)
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_session_reports_typed_topology(environment: tuple[Path, Path]) -> None:
    home, root = environment

    payload = _json(home, "session", str(root))

    assert payload["space"]
    assert payload["repository"]
    assert payload["authority"].endswith("-worktree")


def test_status_renders_provider_records_as_json(
    environment: tuple[Path, Path],
) -> None:
    home, root = environment
    _json(home, "session", str(root))

    payload = _json(home, "status")

    assert [item["relative_path"] for item in payload["authorities"]] == ["."]
    assert payload["parents"] == []
    assert payload["dependencies"] == []
    assert payload["leases"] == []


def test_closure_requires_a_declared_claim(environment: tuple[Path, Path]) -> None:
    home, root = environment
    session = _json(home, "session", str(root))

    result = _run(home, "closure", "--space", session["space"])

    assert result.exit_code != 0
    assert "affected claim" in result.output


def test_permit_is_granted_for_the_reported_closure(
    environment: tuple[Path, Path],
) -> None:
    home, root = environment
    session = _json(home, "session", str(root))
    _json(
        home, "claim", "--space", session["space"], "--authority", session["authority"]
    )

    closure = _json(home, "closure", "--space", session["space"])
    grant = _json(
        home,
        "permit",
        "--space",
        session["space"],
        "--fingerprint",
        closure["fingerprint"],
    )

    assert closure["lockable"] is True
    assert grant["authorities"] == [session["authority"]]


def test_permit_refuses_a_stale_fingerprint(environment: tuple[Path, Path]) -> None:
    home, root = environment
    session = _json(home, "session", str(root))
    _json(
        home, "claim", "--space", session["space"], "--authority", session["authority"]
    )
    stale = _json(home, "closure", "--space", session["space"])["fingerprint"]
    _json(
        home,
        "claim",
        "--space",
        session["space"],
        "--repository",
        session["repository"],
    )

    result = _run(home, "permit", "--space", session["space"], "--fingerprint", stale)

    assert result.exit_code != 0
    assert "changed" in result.output


@pytest.mark.parametrize(
    ("command", "arguments"),
    [
        ("cleanup", ("--repository",)),
        ("abandon", ("--repository",)),
        ("force-release", ()),
    ],
)
def test_destructive_commands_require_explicit_authority(
    environment: tuple[Path, Path],
    command: str,
    arguments: tuple[str, ...],
) -> None:
    home, root = environment
    session = _json(home, "session", str(root))
    extra: list[str] = []
    for option in arguments:
        extra.extend((option, session["repository"]))

    result = _run(home, command, "--space", session["space"], *extra)

    assert result.exit_code != 0
    assert "explicit authority" in result.output


def test_relate_requires_exactly_one_relationship_kind(
    environment: tuple[Path, Path],
) -> None:
    home, _ = environment

    result = _run(home, "relate", "--child", "a")

    assert result.exit_code != 0
    assert "exactly one" in result.output
