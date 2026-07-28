import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.check_skill_distribution import DistributionError, check_distribution


def _write_skill(root: Path) -> None:
    (root / "agents").mkdir(parents=True)
    (root / "references").mkdir()
    (root / "SKILL.md").write_text(
        "Read [commands](references/commands.md).\n", encoding="utf-8"
    )
    (root / "agents" / "openai.yaml").write_text("interface: {}\n", encoding="utf-8")
    (root / "references" / "commands.md").write_text("# Commands\n", encoding="utf-8")


def test_distribution_matches_authoritative_skill_exactly(tmp_path: Path) -> None:
    source = tmp_path / "source"
    distribution = tmp_path / "distribution"
    _write_skill(source)
    _write_skill(distribution)

    check_distribution(source, distribution)


def test_distribution_rejects_extra_repository_content(tmp_path: Path) -> None:
    source = tmp_path / "source"
    distribution = tmp_path / "distribution"
    _write_skill(source)
    _write_skill(distribution)
    (distribution / "zpp").mkdir()
    (distribution / "zpp" / "core.py").write_text("", encoding="utf-8")

    with pytest.raises(DistributionError, match="unexpected files: zpp/core.py"):
        check_distribution(source, distribution)


def test_distribution_requires_every_declared_reference(tmp_path: Path) -> None:
    source = tmp_path / "source"
    distribution = tmp_path / "distribution"
    _write_skill(source)
    (source / "SKILL.md").write_text(
        "Read [commands](references/commands.md) and "
        "[concepts](references/concepts.md).\n",
        encoding="utf-8",
    )
    _write_skill(distribution)

    with pytest.raises(DistributionError, match="missing declared resource"):
        check_distribution(source, distribution)


def test_workflow_validates_and_checks_before_push() -> None:
    workflow = Path(".github/workflows/publish-learn-zpp.yml").read_text(
        encoding="utf-8"
    )

    assert "if: github.ref == 'refs/heads/main'" in workflow
    validator = workflow.index("quick_validate.py")
    split = workflow.index("git subtree split --prefix=skills/learn-zpp")
    layout_check = workflow.index("python scripts/check_skill_distribution.py", split)
    push = workflow.index("git push")

    assert validator < split < layout_check < push


def test_subtree_split_places_only_skill_contents_at_branch_root(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    source = repository / "skills" / "learn-zpp"
    distribution = tmp_path / "distribution"
    shutil.copytree(Path("skills/learn-zpp"), source)

    subprocess.run(["git", "init", "-q", repository], check=True)
    subprocess.run(
        ["git", "-C", repository, "config", "core.autocrlf", "false"], check=True
    )
    subprocess.run(["git", "-C", repository, "add", "skills/learn-zpp"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            repository,
            "-c",
            "user.name=zpp tests",
            "-c",
            "user.email=zpp-tests@example.invalid",
            "commit",
            "-qm",
            "test: add skill",
        ],
        check=True,
    )
    split_commit = subprocess.check_output(
        ["git", "-C", repository, "subtree", "split", "--prefix=skills/learn-zpp"],
        text=True,
    ).strip()
    subprocess.run(
        [
            "git",
            "-C",
            repository,
            "worktree",
            "add",
            "--detach",
            distribution,
            split_commit,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    check_distribution(source, distribution)
