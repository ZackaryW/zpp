from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from zpp.core.errors import ZppDomainError
from zpp.utils.behavior_git import (
    collect_local_changed_paths,
    collect_revision_changed_paths,
    discover_worktree_root,
)
from zpp.utils.behavior_mapping import (
    ArgvProvider,
    BehaviorTarget,
    NxProvider,
    dump_behavior_scaffold,
    load_behavior_mapping,
)
from zpp.utils.behavior_selection import expand_target_argv, select_affected_targets
from zpp.utils.nx_provider import (
    NxSurface,
    build_nx_argv,
    discover_nx_executable,
    inspect_nx_surface,
)
from zpp.utils.processes import ProcessResult, run_process


BEHAVIOR_MAPPING_NAME = "zpp.behave.yaml"


@dataclass(frozen=True, slots=True)
class BehaviorInitializationReport:
    root: Path
    created: bool
    nx_executable: Path | None
    nx_surface: NxSurface | None
    nx_diagnostic: str | None = None


@dataclass(frozen=True, slots=True)
class BehaviorExecutionReport:
    root: Path
    command: str
    targets: tuple[BehaviorTarget, ...]
    result: ProcessResult | None


def initialize_behavior(start: Path) -> BehaviorInitializationReport:
    root = discover_worktree_root(start)
    created = dump_behavior_scaffold(root / BEHAVIOR_MAPPING_NAME)
    executable = discover_nx_executable(root)
    if executable is None:
        return BehaviorInitializationReport(root, created, None, None)
    try:
        surface = inspect_nx_surface(executable, root)
    except ValueError as error:
        return BehaviorInitializationReport(
            root, created, executable, None, str(error)
        )
    return BehaviorInitializationReport(root, created, executable, surface)


def execute_behavior(
    start: Path,
    command_name: str,
    *,
    complete: bool = False,
    base: str | None = None,
    head: str | None = None,
) -> BehaviorExecutionReport:
    if (base is None) != (head is None):
        raise ZppDomainError("--base and --head must be supplied together")

    root = discover_worktree_root(start)
    mapping = load_behavior_mapping(root / BEHAVIOR_MAPPING_NAME)
    command = mapping.commands.get(command_name)
    if command is None:
        raise ZppDomainError(f"behavior command is not declared: {command_name}")

    if complete:
        targets = tuple(command.targets.values())
    else:
        changed = (
            collect_local_changed_paths(root)
            if base is None or head is None
            else collect_revision_changed_paths(root, base, head)
        )
        targets = select_affected_targets(command, changed)

    if not targets:
        return BehaviorExecutionReport(root, command_name, (), None)

    values = tuple(target.value for target in targets)
    if isinstance(command.provider, ArgvProvider):
        argv = expand_target_argv(command.provider.argv, values)
    else:
        argv = _nx_argv(root, command.provider, values)
    result = run_process(argv, cwd=root)
    return BehaviorExecutionReport(root, command_name, targets, result)


def _nx_argv(root: Path, provider: NxProvider, projects: tuple[str, ...]) -> tuple[str, ...]:
    executable = discover_nx_executable(root)
    if executable is None:
        raise ZppDomainError("configured Nx provider is unavailable")
    surface = inspect_nx_surface(executable, root)
    missing = tuple(
        project
        for project in projects
        if project not in surface.projects or provider.target not in surface.projects[project]
    )
    if missing:
        raise ZppDomainError(
            "configured Nx project/target surface is unavailable: "
            + ", ".join(f"{project}:{provider.target}" for project in missing)
        )
    return build_nx_argv(executable, provider, projects)
