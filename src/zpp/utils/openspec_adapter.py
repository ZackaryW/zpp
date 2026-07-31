from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal, Mapping, Sequence

from zpp.utils.processes import ProcessResult, run_process


@dataclass(frozen=True, slots=True)
class OpenSpecMember:
    name: str
    path: Path


@dataclass(frozen=True, slots=True)
class OpenSpecWorkset:
    name: str
    members: tuple[OpenSpecMember, ...]


@dataclass(frozen=True, slots=True)
class OpenSpecStoreRelation:
    store_id: str
    root: Path
    role: Literal["governing", "reference"]


def _require_success(result: ProcessResult) -> ProcessResult:
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"OpenSpec command failed: {detail}")
    return result


def _json(result: ProcessResult) -> dict[str, object]:
    _require_success(result)
    try:
        value = json.loads(result.stdout)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("OpenSpec returned invalid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("OpenSpec returned invalid JSON object")
    return value


def _member(value: object) -> OpenSpecMember:
    if not isinstance(value, dict):
        raise ValueError("OpenSpec returned an invalid workset member")
    name = value.get("name")
    path = value.get("path")
    if not isinstance(name, str) or not name or not isinstance(path, str) or not path:
        raise ValueError("OpenSpec returned an invalid workset member")
    return OpenSpecMember(name=name, path=Path(path).resolve())


def _workset(value: object) -> OpenSpecWorkset:
    if not isinstance(value, dict):
        raise ValueError("OpenSpec returned an invalid workset")
    name = value.get("name")
    members = value.get("members")
    if not isinstance(name, str) or not name or not isinstance(members, list):
        raise ValueError("OpenSpec returned an invalid workset")
    return OpenSpecWorkset(name=name, members=tuple(_member(item) for item in members))


def list_openspec_worksets(
    *,
    env: Mapping[str, str] | None = None,
) -> tuple[OpenSpecWorkset, ...]:
    payload = _json(run_process(("openspec", "workset", "list", "--json"), env=env))
    worksets = payload.get("worksets")
    if not isinstance(worksets, list):
        raise ValueError("OpenSpec returned an invalid workset list")
    return tuple(_workset(item) for item in worksets)


def create_openspec_workset(
    name: str,
    members: Sequence[OpenSpecMember],
    *,
    env: Mapping[str, str] | None = None,
) -> OpenSpecWorkset:
    arguments = ["openspec", "workset", "create", name]
    for member in members:
        arguments.extend(("--member", f"{member.name}={member.path}"))
    arguments.append("--json")
    payload = _json(run_process(arguments, env=env))
    if "workset" not in payload:
        raise ValueError("OpenSpec returned no created workset")
    return _workset(payload["workset"])


def remove_openspec_workset(
    name: str,
    *,
    env: Mapping[str, str] | None = None,
) -> None:
    _require_success(
        run_process(
            ("openspec", "workset", "remove", name, "--yes", "--json"),
            env=env,
        )
    )


def open_openspec_workset(
    name: str,
    *,
    tool: str | None = None,
    env: Mapping[str, str] | None = None,
) -> int:
    arguments = ["openspec", "workset", "open", name]
    if tool is not None:
        arguments.extend(("--tool", tool))
    return run_process(arguments, env=env).returncode


def _store_id(value: dict[str, object]) -> str | None:
    store = value.get("store")
    if isinstance(store, dict) and isinstance(store.get("id"), str):
        return store["id"]
    for key in ("storeId", "store_id"):
        if isinstance(value.get(key), str):
            return value[key]
    return None


def resolve_openspec_relations(project: Path) -> tuple[OpenSpecStoreRelation, ...]:
    payload = _json(
        run_process(("openspec", "context", "--json"), cwd=project)
    )
    candidates: list[tuple[object, Literal["governing", "reference"]]] = [
        (payload.get("root"), "governing")
    ]
    members = payload.get("members", [])
    if not isinstance(members, list):
        raise ValueError("OpenSpec returned invalid context members")
    for member in members:
        role: Literal["governing", "reference"] = "governing"
        if isinstance(member, dict) and (
            member.get("relation") == "reference"
            or member.get("role") in {"reference", "reference_only"}
        ):
            role = "reference"
        candidates.append((member, role))

    relations: list[OpenSpecStoreRelation] = []
    for value, role in candidates:
        if not isinstance(value, dict):
            continue
        store_id = _store_id(value)
        path = value.get("path")
        if store_id is None or not isinstance(path, str) or not path:
            continue
        relations.append(
            OpenSpecStoreRelation(store_id=store_id, root=Path(path).resolve(), role=role)
        )
    return tuple(relations)


def register_private_store(
    store_id: str,
    root: Path,
    *,
    env: Mapping[str, str],
) -> None:
    _require_success(
        run_process(
            (
                "openspec",
                "store",
                "register",
                str(root),
                "--id",
                store_id,
                "--yes",
                "--json",
            ),
            env=env,
        )
    )
