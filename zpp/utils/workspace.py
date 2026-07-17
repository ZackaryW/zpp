"""Read .code-workspace files (JSONC). zpp never writes them."""

import json
import re
from pathlib import Path


def _strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments and trailing commas, string-aware."""
    out: list[str] = []
    i, n, in_str = 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            i = text.find("*/", i + 2)
            i = n if i < 0 else i + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load_members(workspace_file: Path) -> list[dict]:
    """Folders resolved to [{name, path}] with absolute paths, anchored at the
    workspace file's own directory (VSCode semantics). `labeled` records
    whether the folder carried an explicit name (stable key for sync)."""
    data = json.loads(_strip_jsonc(workspace_file.read_text()))
    members = []
    for folder in data.get("folders", []):
        path = (workspace_file.parent / folder["path"]).resolve()
        members.append(
            {
                "name": folder.get("name", path.name),
                "path": str(path),
                "labeled": "name" in folder,
            }
        )
    return members
