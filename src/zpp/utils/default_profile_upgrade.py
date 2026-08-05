from __future__ import annotations

import json
from pathlib import PurePosixPath

from zpp.utils.control_documents import validate_layer_config, validate_trigger_config
from zpp.utils.models import (
    AuthoredLayerFile,
    AuthoredLayerSnapshot,
    ManagedStateError,
    ZppValidationError,
)
from zpp.utils.trait_documents import parse_trait_document


def plan_default_profile_upgrade(
    existing: AuthoredLayerSnapshot | None,
    packaged: AuthoredLayerSnapshot,
) -> AuthoredLayerSnapshot | None:
    _validate_snapshot(packaged, subject="packaged default")
    if existing is None:
        return packaged
    _validate_snapshot(existing, subject="persistent default")

    current = _file_map(existing)
    packaged_files = _file_map(packaged)
    changed = False

    current_triggers = json.loads(current[PurePosixPath("trait.json")])
    packaged_triggers = json.loads(packaged_files[PurePosixPath("trait.json")])
    existing_names = {item["trait"] for item in current_triggers}
    missing_triggers = [
        item for item in packaged_triggers if item["trait"] not in existing_names
    ]
    if missing_triggers:
        current_triggers.extend(missing_triggers)
        current[PurePosixPath("trait.json")] = (
            json.dumps(current_triggers, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        changed = True

    for path, content in packaged_files.items():
        if path.parts[:1] != ("traits",) or path in current:
            continue
        current[path] = content
        changed = True

    if not changed:
        return None

    ordered_paths = (
        PurePosixPath("config.json"),
        PurePosixPath("trait.json"),
        *sorted(path for path in current if path.parts[:1] == ("traits",)),
    )
    merged = AuthoredLayerSnapshot(
        tuple(AuthoredLayerFile(path, current[path]) for path in ordered_paths)
    )
    _validate_snapshot(merged, subject="persistent default upgrade")
    return merged


def _file_map(snapshot: AuthoredLayerSnapshot) -> dict[PurePosixPath, bytes]:
    result: dict[PurePosixPath, bytes] = {}
    for item in snapshot.files:
        if item.relative_path in result:
            raise ManagedStateError(
                f"persistent default contains duplicate path: {item.relative_path}"
            )
        result[item.relative_path] = item.content
    return result


def _validate_snapshot(snapshot: AuthoredLayerSnapshot, *, subject: str) -> None:
    try:
        source = _file_map(snapshot)
        config = source[PurePosixPath("config.json")]
        triggers = source[PurePosixPath("trait.json")]
        validate_layer_config(json.loads(config.decode("utf-8")))
        validate_trigger_config(json.loads(triggers.decode("utf-8")))
        for path, content in source.items():
            if path in {PurePosixPath("config.json"), PurePosixPath("trait.json")}:
                continue
            if len(path.parts) != 2 or path.parts[0] != "traits" or path.suffix != ".md":
                raise ValueError(f"unexpected authored path: {path}")
            parse_trait_document(
                content.decode("utf-8"), expected_name=path.stem
            )
    except (
        KeyError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
        ZppValidationError,
    ) as error:
        raise ManagedStateError(f"{subject} is invalid: {error}") from error
