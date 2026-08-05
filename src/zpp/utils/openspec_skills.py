from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from zpp.utils.models import AgentName, ManagedStateError
from zpp.utils.processes import ProcessResult, run_process
from zpp.utils.skill_bundles import SkillFile, fingerprint_skill_files


OPENSPEC_CORE_SKILL_NAMES = (
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-explore",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-update-change",
)


class ProcessRunner(Protocol):
    def __call__(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> ProcessResult: ...


@dataclass(frozen=True, slots=True)
class GeneratedOpenSpecBundle:
    agent: AgentName
    version: str | None
    files: tuple[SkillFile, ...]
    fingerprint: str


def detect_openspec_version(run: ProcessRunner = run_process) -> str | None:
    try:
        result = run(("openspec", "--version"))
    except OSError:
        return None
    if result.returncode != 0:
        return None
    version = result.stdout.strip()
    return version or None


def generate_openspec_skill_bundles(
    agents: Iterable[AgentName],
    *,
    detected_version: str | None,
    temporary_parent: Path | None = None,
    run: ProcessRunner = run_process,
) -> tuple[GeneratedOpenSpecBundle, ...]:
    selected = tuple(dict.fromkeys(agents))
    if not selected:
        return ()
    parent = str(temporary_parent) if temporary_parent is not None else None
    with TemporaryDirectory(prefix="zpp-openspec-", dir=parent) as temporary:
        temporary_root = Path(temporary)
        project = temporary_root / "project"
        data_root = temporary_root / "openspec-data"
        project.mkdir()
        arguments = (
            "openspec",
            "init",
            ".",
            "--tools",
            ",".join(selected),
            "--force",
            "--no-animation",
        )
        try:
            result = run(
                arguments,
                cwd=project,
                env={"XDG_DATA_HOME": str(data_root)},
            )
        except OSError as error:
            raise ManagedStateError(f"OpenSpec generation failed: {error}") from error
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise ManagedStateError(f"OpenSpec generation failed: {detail}")

        bundles: list[GeneratedOpenSpecBundle] = []
        for agent in selected:
            root = project / _generated_relative_root(agent)
            files = _collect_generated_skills(root)
            bundles.append(
                GeneratedOpenSpecBundle(
                    agent,
                    detected_version,
                    files,
                    fingerprint_skill_files(files),
                )
            )
        return tuple(bundles)


def _generated_relative_root(agent: AgentName) -> Path:
    if agent == "codex":
        return Path(".codex/skills")
    if agent == "pi":
        return Path(".pi/skills")
    return Path(".claude/skills")


def _collect_generated_skills(root: Path) -> tuple[SkillFile, ...]:
    if root.is_symlink() or not root.is_dir():
        raise ManagedStateError(f"OpenSpec did not generate a skill root: {root}")
    names = tuple(sorted(path.name for path in root.iterdir()))
    if names != OPENSPEC_CORE_SKILL_NAMES:
        raise ManagedStateError("OpenSpec generated an unexpected core skill inventory")

    files: list[SkillFile] = []
    for name in OPENSPEC_CORE_SKILL_NAMES:
        skill = root / name
        document = skill / "SKILL.md"
        if skill.is_symlink() or not skill.is_dir() or not document.is_file():
            raise ManagedStateError(f"OpenSpec generated an invalid skill: {skill}")
        try:
            document.read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise ManagedStateError(f"OpenSpec generated non-UTF-8 guidance: {document}") from error
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise ManagedStateError(f"OpenSpec generated a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(root).as_posix()
                files.append(SkillFile(relative, path.read_bytes()))
            elif not path.is_dir():
                raise ManagedStateError(f"OpenSpec generated invalid content: {path}")
    return tuple(files)
