"""Atomic product-home persistence for active workflow reminders."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID

from zpp.core.workflows import (
    WorkflowContract,
    WorkflowRun,
    WorkflowStageState,
    new_workflow_run,
    workflow_run_to_dict,
)
from zpp.utils.product_home import ZppHome


class WorkflowReminderError(ValueError):
    """Persisted workflow reminder state is invalid or conflicted."""


@dataclass(frozen=True, slots=True)
class StoredWorkflowRun:
    run: WorkflowRun
    token: str


class WorkflowReminderRepository:
    def __init__(
        self,
        home: ZppHome,
        *,
        known_components: frozenset[str],
    ) -> None:
        self._home = home
        self._known_components = known_components

    def load(self, *, root: Path, change: str) -> StoredWorkflowRun | None:
        normalized = _normalized_root(root)
        path = self._path(normalized, change)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            return None
        run = _decode_run(raw, source=path, known_components=self._known_components)
        if run.root != normalized or run.change != change:
            raise WorkflowReminderError(f"{path}: workflow target does not match key")
        return StoredWorkflowRun(run, _token(raw))

    def list_for_root(self, *, root: Path) -> tuple[StoredWorkflowRun, ...]:
        normalized = _normalized_root(root)
        directory = self._home.workflow_reminder_root
        if not directory.is_dir():
            return ()
        selected: list[StoredWorkflowRun] = []
        for path in sorted(directory.glob("*.json"), key=lambda item: item.name):
            raw = path.read_bytes()
            run = _decode_run(
                raw,
                source=path,
                known_components=self._known_components,
            )
            if run.root == normalized:
                selected.append(StoredWorkflowRun(run, _token(raw)))
        return tuple(sorted(selected, key=lambda item: item.run.change))

    def start(
        self,
        contract: WorkflowContract,
        *,
        root: Path,
        change: str,
    ) -> StoredWorkflowRun:
        normalized = _normalized_root(root)
        existing = self.load(root=normalized, change=change)
        if existing is not None:
            if existing.run.workflow != contract.name:
                raise WorkflowReminderError(
                    f"targets already use workflow {existing.run.workflow!r}"
                )
            return existing
        run = new_workflow_run(contract, root=normalized, change=change)
        _validate_run(run, self._known_components)
        raw = _encode_run(run)
        path = self._path(normalized, change)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not _write_new_atomic(path, raw):
            raced = self.load(root=normalized, change=change)
            if raced is None:
                raise WorkflowReminderError("workflow creation race lost without state")
            if raced.run.workflow != contract.name:
                raise WorkflowReminderError(
                    f"targets already use workflow {raced.run.workflow!r}"
                )
            return raced
        return StoredWorkflowRun(run, _token(raw))

    def save(
        self, stored: StoredWorkflowRun, candidate: WorkflowRun
    ) -> StoredWorkflowRun:
        _validate_run(candidate, self._known_components)
        if (
            candidate.run_id != stored.run.run_id
            or candidate.root != stored.run.root
            or candidate.change != stored.run.change
            or candidate.workflow != stored.run.workflow
        ):
            raise WorkflowReminderError("replacement changes workflow identity")
        path = self._path(candidate.root, candidate.change)
        try:
            current = path.read_bytes()
        except FileNotFoundError as error:
            raise WorkflowReminderError("workflow reminder is absent") from error
        if _token(current) != stored.token:
            raise WorkflowReminderError("stale workflow reminder write")
        raw = _encode_run(candidate)
        _replace_atomic(path, raw)
        return StoredWorkflowRun(candidate, _token(raw))

    def stop(self, *, root: Path, change: str) -> bool:
        normalized = _normalized_root(root)
        path = self._path(normalized, change)
        try:
            path.unlink()
        except FileNotFoundError:
            return False
        return True

    def _path(self, root: Path, change: str) -> Path:
        if not change:
            raise WorkflowReminderError("change must be non-empty")
        digest = sha256((str(root) + "\0" + change).encode("utf-8")).hexdigest()
        return self._home.workflow_reminder_root / f"{digest}.json"


def _normalized_root(root: Path) -> Path:
    return Path(os.path.abspath(os.fspath(root.expanduser())))


def _token(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _encode_run(run: WorkflowRun) -> bytes:
    return (
        json.dumps(
            workflow_run_to_dict(run),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _decode_run(
    raw: bytes,
    *,
    source: Path,
    known_components: frozenset[str],
) -> WorkflowRun:
    try:
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("workflow reminder must be an object")
        expected = {
            "version",
            "run_id",
            "workflow",
            "root",
            "change",
            "stages",
            "observed_bundle",
        }
        if set(value) != expected:
            raise ValueError("workflow reminder has invalid fields")
        if value["version"] != 1 or isinstance(value["version"], bool):
            raise ValueError("workflow reminder version must be integer 1")
        stages_value = value["stages"]
        if not isinstance(stages_value, list):
            raise ValueError("workflow reminder stages must be an array")
        stages = tuple(_decode_stage(item) for item in stages_value)
        bundle_value = value["observed_bundle"]
        run = WorkflowRun(
            UUID(_string(value, "run_id")),
            _string(value, "workflow"),
            Path(_string(value, "root")),
            _string(value, "change"),
            stages,
            UUID(bundle_value) if isinstance(bundle_value, str) else None,
        )
        if bundle_value is not None and not isinstance(bundle_value, str):
            raise ValueError("observed_bundle must be a UUID string or null")
        _validate_run(run, known_components)
        return run
    except (KeyError, TypeError, UnicodeError, ValueError) as error:
        if isinstance(error, WorkflowReminderError):
            raise
        raise WorkflowReminderError(f"{source}: {error}") from error


def _decode_stage(value: object) -> WorkflowStageState:
    if not isinstance(value, dict) or set(value) != {
        "id",
        "component",
        "status",
        "result",
    }:
        raise ValueError("workflow reminder stage has invalid fields")
    status = value["status"]
    if status not in {"pending", "completed", "skipped"}:
        raise ValueError("workflow reminder stage status is invalid")
    result = value["result"]
    if result is not None and not isinstance(result, str):
        raise ValueError("workflow reminder stage result is invalid")
    return WorkflowStageState(
        _string(value, "id"),
        _string(value, "component"),
        status,
        result,
    )


def _string(value: dict[str, Any], field: str) -> str:
    selected = value[field]
    if not isinstance(selected, str) or not selected:
        raise ValueError(f"{field} must be a non-empty string")
    return selected


def _validate_run(run: WorkflowRun, known_components: frozenset[str]) -> None:
    if not run.workflow or not run.change or not run.stages:
        raise WorkflowReminderError(
            "workflow reminder identity and stages are required"
        )
    ids = [stage.id for stage in run.stages]
    duplicates = sorted({stage_id for stage_id in ids if ids.count(stage_id) > 1})
    if duplicates:
        raise WorkflowReminderError(f"duplicate stage id: {duplicates[0]}")
    unknown = sorted(
        {
            stage.component
            for stage in run.stages
            if stage.component not in known_components
        }
    )
    if unknown:
        raise WorkflowReminderError(f"unknown component: {unknown[0]}")


def _temporary_path(path: Path, raw: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _write_new_atomic(path: Path, raw: bytes) -> bool:
    temporary = _temporary_path(path, raw)
    try:
        try:
            os.link(temporary, path)
        except FileExistsError:
            return False
        return True
    finally:
        temporary.unlink(missing_ok=True)


def _replace_atomic(path: Path, raw: bytes) -> None:
    temporary = _temporary_path(path, raw)
    try:
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
