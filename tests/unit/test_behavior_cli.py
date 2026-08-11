import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from zpp.cli import app

runner = CliRunner()


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", *arguments),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "--quiet")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "user.name", "Test")
    (root / "tracked.txt").write_text("base\n")
    git(root, "add", ".")
    git(root, "commit", "--quiet", "-m", "base")
    return root


def test_behavior_init_uses_the_git_root_and_dedicated_yaml(
    tmp_path: Path, monkeypatch
) -> None:
    root = repository(tmp_path)
    nested = root / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "behave", "init"],
    )

    assert result.exit_code == 0, result.output
    assert "Behavior mapping created" in result.stdout
    content = (root / "zpp.behave.yaml").read_text()
    assert "version: 1" in content
    assert "zpp.behave:" not in content


def test_behavior_all_forwards_provider_output_and_targets(
    tmp_path: Path, monkeypatch
) -> None:
    root = repository(tmp_path)
    (root / "zpp.behave.yaml").write_text(
        f"""version: 1
commands:
  bdd:
    provider:
      kind: argv
      argv:
        - {sys.executable!r}
        - -c
        - "import sys; print('|'.join(sys.argv[1:]))"
        - "{{targets}}"
    targets:
      core: {{value: features/core, paths: [src/core/**]}}
      workflow: {{value: features/workflow, paths: [src/workflow/**]}}
"""
    )
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "behave", "bdd", "--all"],
    )

    assert result.exit_code == 0, result.output
    assert result.stdout == "features/core|features/workflow\n"


def test_behavior_init_preserves_an_existing_version_one_mapping(
    tmp_path: Path, monkeypatch
) -> None:
    root = repository(tmp_path)
    path = root / "zpp.behave.yaml"
    authored = """version: 1
commands:
  bdd:
    provider: {kind: argv, argv: [runner, "{targets}"]}
    targets:
      core: {value: features/core, paths: [src/core/**]}
"""
    path.write_text(authored)
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "behave", "init"],
    )

    assert result.exit_code == 0, result.output
    assert "Behavior mapping validated" in result.stdout
    assert path.read_text() == authored


def test_behavior_rejects_ambiguous_selection_before_repository_access() -> None:
    result = runner.invoke(
        app,
        ["behave", "bdd", "--all", "--target", "core"],
    )

    assert result.exit_code == 2
    assert "mutually exclusive" in result.output


def test_behavior_revision_range_selects_declared_affected_targets(
    tmp_path: Path, monkeypatch
) -> None:
    root = repository(tmp_path)
    base = git(root, "rev-parse", "HEAD")
    changed = root / "src" / "core" / "module.py"
    changed.parent.mkdir(parents=True)
    changed.write_text("changed\n")
    git(root, "add", ".")
    git(root, "commit", "--quiet", "-m", "change core")
    head = git(root, "rev-parse", "HEAD")
    (root / "zpp.behave.yaml").write_text(
        f"""version: 1
commands:
  bdd:
    provider:
      kind: argv
      argv:
        - {sys.executable!r}
        - -c
        - "import sys; print('|'.join(sys.argv[1:]))"
        - "{{targets}}"
    targets:
      core: {{value: features/core, paths: [src/core/**]}}
      workflow: {{value: features/workflow, paths: [src/workflow/**]}}
"""
    )
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        [
            "--path",
            str(tmp_path / "state"),
            "behave",
            "bdd",
            "--base",
            base,
            "--head",
            head,
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.stdout == "features/core\n"


def test_behavior_propagates_the_provider_exit_code(
    tmp_path: Path, monkeypatch
) -> None:
    root = repository(tmp_path)
    (root / "zpp.behave.yaml").write_text(
        f"""version: 1
commands:
  bdd:
    provider:
      kind: argv
      argv: [{sys.executable!r}, -c, "raise SystemExit(7)", "{{targets}}"]
    targets:
      core: {{value: features/core, paths: [src/core/**]}}
"""
    )
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "behave", "bdd", "--all"],
    )

    assert result.exit_code == 7
