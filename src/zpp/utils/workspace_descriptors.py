from __future__ import annotations

import json
from pathlib import Path

from zpp.utils.openspec_adapter import OpenSpecMember


def load_code_workspace(path: Path) -> tuple[OpenSpecMember, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{path} contains invalid JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("folders"), list):
        raise ValueError(f"{path} contains no valid folders list")

    members: list[OpenSpecMember] = []
    for value in payload["folders"]:
        if not isinstance(value, dict) or not isinstance(value.get("path"), str):
            raise ValueError(f"{path} contains an invalid workspace member")
        raw_path = Path(value["path"])
        member_path = raw_path if raw_path.is_absolute() else path.parent / raw_path
        member_path = member_path.resolve()
        if not member_path.is_dir():
            raise ValueError(f"{member_path} is not an existing directory")
        raw_name = value.get("name")
        if raw_name is not None and (not isinstance(raw_name, str) or not raw_name):
            raise ValueError(f"{path} contains an invalid workspace member name")
        members.append(OpenSpecMember(raw_name or member_path.name, member_path))
    return tuple(members)
