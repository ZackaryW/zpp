from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
from collections.abc import Sequence

from zpp.utils.behavior_mapping import NxProvider
from zpp.utils.models import ManagedStateError
from zpp.utils.processes import ProcessResult, run_process


@dataclass(frozen=True, slots=True)
class NxSurface:
    projects: dict[str, frozenset[str]]


def discover_nx_executable(root: Path) -> Path | None:
    package_names = ("nx.cmd", "nx") if os.name == "nt" else ("nx", "nx.cmd")
    candidates = [
        *(root / "node_modules" / ".bin" / name for name in package_names),
        root / ("nx.bat" if os.name == "nt" else "nx"),
    ]
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate.resolve()
    available = shutil.which("nx")
    return None if available is None else Path(available).resolve()


def inspect_nx_surface(executable: Path, root: Path) -> NxSurface:
    projects_result = run_process(
        (str(executable), "show", "projects", "--json"), cwd=root
    )
    projects_raw = _load_json(projects_result)
    if not isinstance(projects_raw, list) or not all(
        isinstance(project, str) and project for project in projects_raw
    ):
        raise ManagedStateError("Nx workspace surface returned an invalid project list")

    projects: dict[str, frozenset[str]] = {}
    for project in projects_raw:
        result = run_process(
            (str(executable), "show", "project", project, "--json"), cwd=root
        )
        raw = _load_json(result)
        if not isinstance(raw, dict) or not isinstance(raw.get("targets"), dict):
            raise ManagedStateError(
                f"Nx workspace surface returned invalid project data for {project}"
            )
        targets = raw["targets"]
        if not all(isinstance(name, str) and name for name in targets):
            raise ManagedStateError(
                f"Nx workspace surface returned invalid targets for {project}"
            )
        projects[project] = frozenset(targets)
    return NxSurface(projects)


def build_nx_argv(
    executable: Path, provider: NxProvider, projects: Sequence[str]
) -> tuple[str, ...]:
    return (
        str(executable),
        "run-many",
        "--target",
        provider.target,
        "--projects",
        ",".join(projects),
        *provider.args,
    )


def _load_json(result: ProcessResult) -> object:
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).strip()
        raise ManagedStateError(
            f"Nx workspace surface inspection failed: {diagnostic or result.returncode}"
        )
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as error:
        raise ManagedStateError("Nx workspace surface returned invalid JSON") from error
