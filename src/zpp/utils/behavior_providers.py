from __future__ import annotations

import json
import os
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from openlease.utils.processes import ProcessRunner, SubprocessRunner
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from zpp.core.behavior import BehaviorProviderAdapter, BehaviorProviderError
from zpp.utils.repository_paths import (
    RepositoryPathError,
    resolve_repository_file,
)

TARGET_MARKER = "{targets}"


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ArgvSettings(_ClosedModel):
    kind: Literal["argv"]
    argv: list[str] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_argv(self) -> ArgvSettings:
        if self.argv.count(TARGET_MARKER) != 1 or self.argv[0] == TARGET_MARKER:
            raise ValueError(
                "argv provider requires exactly one target expansion position"
            )
        if any(not value or "\x00" in value for value in self.argv):
            raise ValueError("argv provider values must be non-empty and NUL-free")
        return self


class ArgvAdapter:
    kind = "argv"

    def validate(self, raw: Mapping[str, object]) -> ArgvSettings:
        return _validate_model(ArgvSettings, raw)

    def argv(
        self,
        root: Path,
        settings: object,
        targets: tuple[str, ...],
    ) -> tuple[str, ...]:
        del root
        if not isinstance(settings, ArgvSettings):
            raise BehaviorProviderError("invalid argv adapter settings")
        marker = settings.argv.index(TARGET_MARKER)
        return (
            *settings.argv[:marker],
            *targets,
            *settings.argv[marker + 1 :],
        )


class NxSettings(_ClosedModel):
    kind: Literal["nx"]
    target: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_literals(self) -> NxSettings:
        if "\x00" in self.target or self.target.startswith("-"):
            raise ValueError("Nx target must be a safe non-option value")
        if TARGET_MARKER in self.args or any(
            not value or "\x00" in value for value in self.args
        ):
            raise ValueError("Nx arguments must be non-empty literal values")
        return self


class NxAdapter:
    kind = "nx"

    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self.runner = runner or SubprocessRunner()

    def validate(self, raw: Mapping[str, object]) -> NxSettings:
        return _validate_model(NxSettings, raw)

    def argv(
        self, root: Path, settings: object, targets: tuple[str, ...]
    ) -> tuple[str, ...]:
        if not isinstance(settings, NxSettings):
            raise BehaviorProviderError("invalid Nx adapter settings")
        executable = _discover_nx(root)
        if executable is None:
            raise BehaviorProviderError("configured Nx provider is unavailable")
        projects = _inspect_nx(self.runner, executable, root)
        missing = tuple(
            project
            for project in targets
            if project not in projects or settings.target not in projects[project]
        )
        if missing:
            unavailable = ", ".join(
                f"{project}:{settings.target}" for project in missing
            )
            raise BehaviorProviderError(
                f"configured Nx project/target surface is unavailable: {unavailable}"
            )
        return (
            str(executable),
            "run-many",
            "--target",
            settings.target,
            "--projects",
            ",".join(targets),
            *settings.args,
        )


class GoTaskSettings(_ClosedModel):
    kind: Literal["go-task"]
    executable: str | None = None
    args: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_literals(self) -> GoTaskSettings:
        if self.executable is not None and (
            not self.executable or "\x00" in self.executable
        ):
            raise ValueError("Go Task executable selector is invalid")
        if any(not value or "\x00" in value for value in self.args):
            raise ValueError("Go Task arguments must be non-empty literal values")
        return self


class GoTaskAdapter:
    kind = "go-task"

    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self.runner = runner or SubprocessRunner()

    def validate(self, raw: Mapping[str, object]) -> GoTaskSettings:
        return _validate_model(GoTaskSettings, raw)

    def argv(
        self, root: Path, settings: object, targets: tuple[str, ...]
    ) -> tuple[str, ...]:
        if not isinstance(settings, GoTaskSettings):
            raise BehaviorProviderError("invalid Go Task adapter settings")
        if any(
            not target or target.startswith("-") or "\x00" in target
            for target in targets
        ):
            raise BehaviorProviderError("Go Task names must be safe non-option values")
        executable = _discover_task(root, settings.executable)
        available = _inspect_task(self.runner, executable, root)
        missing = tuple(target for target in targets if target not in available)
        if missing:
            raise BehaviorProviderError(
                "configured Go Task surface is unavailable: " + ", ".join(missing)
            )
        return (str(executable), *settings.args, *targets)


def default_behavior_adapters(
    runner: ProcessRunner | None = None,
) -> tuple[BehaviorProviderAdapter, ...]:
    return (ArgvAdapter(), NxAdapter(runner), GoTaskAdapter(runner))


def behavior_provider_diagnostics(root: Path) -> tuple[str, ...]:
    nx = _discover_nx(root)
    task = shutil.which("task")
    return (
        "argv: available",
        "nx: unavailable" if nx is None else f"nx: {nx}",
        "go-task: unavailable" if task is None else f"go-task: {Path(task).resolve()}",
    )


def _validate_model(model: type[_ClosedModel], raw: Mapping[str, object]):
    try:
        return model.model_validate(dict(raw), strict=True)
    except ValidationError as error:
        raise BehaviorProviderError(str(error)) from error


def _discover_nx(root: Path) -> Path | None:
    names = ("nx.cmd", "nx") if os.name == "nt" else ("nx", "nx.cmd")
    for name in names:
        candidate = root / "node_modules" / ".bin" / name
        if candidate.is_file() and not candidate.is_symlink():
            return candidate.resolve()
    installation = root / ".nx" / "installation"
    if installation.is_dir():
        wrapper = root / ("nx.bat" if os.name == "nt" else "nx")
        if wrapper.is_file() and not wrapper.is_symlink():
            return wrapper.resolve()
    available = shutil.which("nx")
    return None if available is None else Path(available).resolve()


def _inspect_nx(
    runner: ProcessRunner, executable: Path, root: Path
) -> dict[str, frozenset[str]]:
    projects_raw = _json_result(
        runner.run((str(executable), "show", "projects", "--json"), cwd=root),
        "Nx project inspection",
    )
    if not isinstance(projects_raw, list) or not all(
        isinstance(project, str) and project for project in projects_raw
    ):
        raise BehaviorProviderError("Nx surface returned an invalid project list")
    projects: dict[str, frozenset[str]] = {}
    for project in projects_raw:
        raw = _json_result(
            runner.run(
                (str(executable), "show", "project", project, "--json"), cwd=root
            ),
            f"Nx project inspection for {project}",
        )
        if not isinstance(raw, dict) or not isinstance(raw.get("targets"), dict):
            raise BehaviorProviderError(
                f"Nx surface returned invalid project data for {project}"
            )
        targets = raw["targets"]
        if not all(isinstance(name, str) and name for name in targets):
            raise BehaviorProviderError(
                f"Nx surface returned invalid targets for {project}"
            )
        projects[project] = frozenset(targets)
    return projects


def _discover_task(root: Path, selector: str | None) -> Path:
    if selector is not None:
        try:
            return resolve_repository_file(root, selector)
        except RepositoryPathError as error:
            raise BehaviorProviderError(str(error)) from error
    available = shutil.which("task")
    if available is None:
        raise BehaviorProviderError("configured Go Task provider is unavailable")
    return Path(available).resolve()


def _inspect_task(
    runner: ProcessRunner, executable: Path, root: Path
) -> frozenset[str]:
    raw = _json_result(
        runner.run((str(executable), "--list-all", "--json"), cwd=root),
        "Go Task surface inspection",
    )
    items = raw.get("tasks") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise BehaviorProviderError("Go Task surface returned an invalid task list")
    names: list[str] = []
    for item in items:
        name = item.get("name") if isinstance(item, dict) else item
        if not isinstance(name, str) or not name:
            raise BehaviorProviderError("Go Task surface returned an invalid task")
        names.append(name)
    return frozenset(names)


def _json_result(result, operation: str) -> object:
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout or str(result.returncode)).strip()
        raise BehaviorProviderError(f"{operation} failed: {diagnostic}")
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as error:
        raise BehaviorProviderError(f"{operation} returned invalid JSON") from error
