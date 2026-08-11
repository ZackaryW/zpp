from __future__ import annotations

import json
import subprocess
from collections.abc import Iterator, Sequence
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from agent_router import Agent, InvalidAssetError, Skill

OPENSPEC_CORE_SKILL_NAMES = (
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-explore",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-update-change",
)


@dataclass(frozen=True, slots=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner(Protocol):
    def __call__(self, argv: tuple[str, ...], *, cwd: Path) -> ProcessResult: ...


class OpenSpecGenerationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class OpenSpecProvenance:
    schema: int
    generator: str
    openspec_version: str


def write_openspec_provenance(
    skill_root: Path,
    provenance: OpenSpecProvenance,
) -> Path:
    version = provenance.openspec_version.strip()
    if not version:
        raise OpenSpecGenerationError("OpenSpec version is required")
    path = skill_root / ".zpp-openspec.json"
    document = {
        "generator": provenance.generator,
        "openspec_version": version,
        "schema": provenance.schema,
    }
    path.write_text(
        json.dumps(document, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return path


def run_process(argv: tuple[str, ...], *, cwd: Path) -> ProcessResult:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    return ProcessResult(argv, completed.returncode, completed.stdout, completed.stderr)


def detect_openspec_version(
    run: ProcessRunner = run_process,
    *,
    cwd: Path | None = None,
) -> str | None:
    working_directory = Path.cwd() if cwd is None else cwd
    try:
        result = run(("openspec", "--version"), cwd=working_directory)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    version = result.stdout.strip()
    return version or None


@contextmanager
def generated_openspec_skills(
    agent: Agent,
    *,
    openspec_version: str,
    run: ProcessRunner = run_process,
) -> Iterator[tuple[Skill, ...]]:
    selected = Agent(agent)
    provenance = OpenSpecProvenance(1, "zpp", openspec_version)
    if not provenance.openspec_version.strip():
        raise OpenSpecGenerationError("OpenSpec version is required")
    with TemporaryDirectory(prefix="zpp-openspec-") as temporary:
        project = Path(temporary) / "project"
        project.mkdir()
        argv = (
            "openspec",
            "init",
            ".",
            "--tools",
            selected.value,
            "--force",
        )
        try:
            result = run(argv, cwd=project)
        except OSError as error:
            raise OpenSpecGenerationError(
                f"OpenSpec generation failed: {error}"
            ) from error
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise OpenSpecGenerationError(f"OpenSpec generation failed: {detail}")
        root = project / _generated_relative_root(selected)
        try:
            names = tuple(sorted(path.name for path in root.iterdir()))
        except OSError as error:
            raise OpenSpecGenerationError(
                f"OpenSpec did not generate a skill root: {root}"
            ) from error
        if names != OPENSPEC_CORE_SKILL_NAMES:
            raise OpenSpecGenerationError(
                "OpenSpec generated an unexpected core skill inventory"
            )
        try:
            for name in names:
                write_openspec_provenance(root / name, provenance)
            skills = tuple(Skill.from_path(root / name) for name in names)
        except InvalidAssetError as error:
            raise OpenSpecGenerationError(
                f"OpenSpec generated an invalid skill: {error}"
            ) from error
        yield skills


@contextmanager
def generated_openspec_skill_sets(
    agents: Sequence[Agent],
    *,
    run: ProcessRunner = run_process,
    cwd: Path | None = None,
) -> Iterator[tuple[tuple[Agent, tuple[Skill, ...]], ...]]:
    selected = tuple(dict.fromkeys(Agent(agent) for agent in agents))
    version = detect_openspec_version(run, cwd=cwd)
    if version is None:
        raise OpenSpecGenerationError("OpenSpec version is required")
    with ExitStack() as stack:
        generated = tuple(
            (
                agent,
                stack.enter_context(
                    generated_openspec_skills(
                        agent,
                        openspec_version=version,
                        run=run,
                    )
                ),
            )
            for agent in selected
        )
        yield generated


def _generated_relative_root(agent: Agent) -> Path:
    return {
        Agent.CODEX: Path(".codex/skills"),
        Agent.CLAUDE: Path(".claude/skills"),
        Agent.PI: Path(".pi/skills"),
        Agent.KIMI: Path(".kimi/skills"),
    }[agent]


__all__ = [
    "OPENSPEC_CORE_SKILL_NAMES",
    "OpenSpecGenerationError",
    "OpenSpecProvenance",
    "ProcessResult",
    "detect_openspec_version",
    "generated_openspec_skill_sets",
    "generated_openspec_skills",
    "write_openspec_provenance",
]
