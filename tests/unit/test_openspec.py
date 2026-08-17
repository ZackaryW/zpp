from __future__ import annotations

from pathlib import Path

import pytest
from agent_router import Agent

from zpp.utils.openspec import (
    OPENSPEC_CORE_SKILL_NAMES,
    OpenSpecGenerationError,
    OpenSpecProvenance,
    ProcessResult,
    detect_openspec_version,
    generated_openspec_skill_sets,
    generated_openspec_skills,
    write_openspec_provenance,
)

GENERATED_ROOTS = {
    Agent.CODEX: Path(".codex/skills"),
    Agent.CLAUDE: Path(".claude/skills"),
    Agent.PI: Path(".pi/skills"),
    Agent.KIMI: Path(".kimi/skills"),
}


def _write_generated(root: Path, agent: Agent) -> None:
    for name in OPENSPEC_CORE_SKILL_NAMES:
        skill = root / GENERATED_ROOTS[agent] / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: generated\n---\n{name}\n",
            encoding="utf-8",
        )


@pytest.mark.parametrize("agent", tuple(Agent))
def test_generation_returns_exact_agent_skills_and_cleans_project(
    agent: Agent,
) -> None:
    projects: list[Path] = []

    def run(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        assert argv == ("openspec", "init", ".", "--tools", agent.value, "--force")
        projects.append(cwd)
        _write_generated(cwd, agent)
        return ProcessResult(argv, 0, "initialized\n", "")

    with generated_openspec_skills(agent, openspec_version="1.7.0", run=run) as skills:
        assert tuple(skill.name for skill in skills) == OPENSPEC_CORE_SKILL_NAMES
        assert all(skill.path.is_dir() for skill in skills)
        assert all(
            ".zpp-openspec.json" in {item.relative_path for item in skill.files}
            for skill in skills
        )
        assert projects[0].exists()

    assert not projects[0].exists()


def test_version_detection_is_explicit_and_unavailable_is_none(
    tmp_path: Path,
) -> None:
    calls: list[tuple[tuple[str, ...], Path]] = []

    def available(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        calls.append((argv, cwd))
        return ProcessResult(argv, 0, "1.7.0\n", "")

    def unavailable(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        return ProcessResult(argv, 1, "", "missing")

    assert detect_openspec_version(available, cwd=tmp_path) == "1.7.0"
    assert calls == [(("openspec", "--version"), tmp_path)]
    assert detect_openspec_version(unavailable, cwd=tmp_path) is None


def test_malformed_generation_fails_and_cleans_project() -> None:
    projects: list[Path] = []

    def run(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        projects.append(cwd)
        partial = cwd / ".codex/skills/openspec-apply-change"
        partial.mkdir(parents=True)
        (partial / "SKILL.md").write_text(
            "---\nname: openspec-apply-change\ndescription: partial\n---\n",
            encoding="utf-8",
        )
        return ProcessResult(argv, 0, "initialized", "")

    with (
        pytest.raises(
            OpenSpecGenerationError,
            match="unexpected core skill inventory",
        ),
        generated_openspec_skills(Agent.CODEX, openspec_version="1.7.0", run=run),
    ):
        pytest.fail("malformed generation yielded")

    assert not projects[0].exists()


def test_provenance_is_deterministic_and_changes_fingerprint(tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    path = write_openspec_provenance(skill, OpenSpecProvenance(1, "zpp", "1.7.0"))

    assert path.read_text(encoding="utf-8") == (
        '{"generator":"zpp","openspec_version":"1.7.0","schema":1}\n'
    )
    with pytest.raises(OpenSpecGenerationError, match="version is required"):
        write_openspec_provenance(skill, OpenSpecProvenance(1, "zpp", "   "))

    def run(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        _write_generated(cwd, Agent.CODEX)
        return ProcessResult(argv, 0, "initialized", "")

    with generated_openspec_skills(
        Agent.CODEX, openspec_version="1.7.0", run=run
    ) as first:
        first_fingerprints = tuple(item.fingerprint for item in first)
    with generated_openspec_skills(
        Agent.CODEX, openspec_version="1.8.0", run=run
    ) as changed:
        changed_fingerprints = tuple(item.fingerprint for item in changed)

    assert first_fingerprints != changed_fingerprints


def test_multi_agent_generation_preserves_order_and_preflights_all(
    tmp_path: Path,
) -> None:
    projects: list[Path] = []

    def run(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        if argv == ("openspec", "--version"):
            assert cwd == tmp_path
            return ProcessResult(argv, 0, "1.7.0\n", "")
        agent = Agent(argv[4])
        projects.append(cwd)
        _write_generated(cwd, agent)
        return ProcessResult(argv, 0, "initialized", "")

    with generated_openspec_skill_sets(
        (Agent.PI, Agent.CODEX, Agent.PI), run=run, cwd=tmp_path
    ) as generated:
        assert tuple(agent for agent, _ in generated) == (Agent.PI, Agent.CODEX)
        assert all(path.exists() for path in projects)
        assert all(len(skills) == 6 for _, skills in generated)

    assert all(not path.exists() for path in projects)


def test_multi_agent_failure_yields_nothing_and_cleans_prior_projects(
    tmp_path: Path,
) -> None:
    projects: list[Path] = []

    def run(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
        if argv == ("openspec", "--version"):
            return ProcessResult(argv, 0, "1.7.0\n", "")
        agent = Agent(argv[4])
        projects.append(cwd)
        if agent is Agent.CODEX:
            _write_generated(cwd, agent)
        return ProcessResult(argv, 0, "initialized", "")

    with (
        pytest.raises(OpenSpecGenerationError, match="OpenSpec"),
        generated_openspec_skill_sets((Agent.CODEX, Agent.PI), run=run, cwd=tmp_path),
    ):
        pytest.fail("partial selected inventories yielded")

    assert all(not path.exists() for path in projects)
