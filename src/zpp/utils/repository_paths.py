from __future__ import annotations

import re
from functools import cache
from pathlib import Path, PurePosixPath


class RepositoryPathError(ValueError):
    """A repository-relative path or pattern is unsafe or unsupported."""


_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def normalize_repository_path(value: str) -> PurePosixPath:
    if (
        not value
        or "\x00" in value
        or "\\" in value
        or value.startswith("/")
        or _WINDOWS_DRIVE.match(value)
    ):
        raise RepositoryPathError(f"invalid repository path: {value!r}")
    path = PurePosixPath(value)
    if (
        path.as_posix() != value
        or value == "."
        or any(part == ".." for part in path.parts)
    ):
        raise RepositoryPathError(f"invalid repository path: {value!r}")
    return path


def validate_repository_glob(value: str) -> str:
    normalize_repository_path(value)
    opened: int | None = None
    for index, character in enumerate(value):
        if character == "[":
            if opened is not None:
                raise RepositoryPathError(
                    "repository glob has nested character classes"
                )
            opened = index
        elif character == "]":
            if opened is None:
                raise RepositoryPathError(
                    "repository glob has an unmatched closing bracket"
                )
            if value[opened + 1 : index] in {"", "!"}:
                raise RepositoryPathError(
                    "repository glob has an empty character class"
                )
            opened = None
    if opened is not None:
        raise RepositoryPathError("repository glob has an unclosed character class")
    try:
        glob_full_match("", value)
    except re.error as error:
        raise RepositoryPathError(f"invalid repository glob: {error}") from error
    return value


def glob_full_match(path: str, pattern: str) -> bool:
    return _compiled_glob(pattern).match(path) is not None


@cache
def _compiled_glob(pattern: str) -> re.Pattern[str]:
    segments = pattern.split("/")
    parts: list[str] = []
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        if segment == "**":
            parts.append(".*" if last else "(?:.*/)?")
        else:
            parts.append(_translate_segment(segment))
            if not last:
                parts.append("/")
    return re.compile("".join(parts) + r"\Z")


def _translate_segment(segment: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(segment):
        character = segment[index]
        if character == "*":
            result.append("[^/]*")
            index += 1
        elif character == "?":
            result.append("[^/]")
            index += 1
        elif character == "[":
            end = segment.index("]", index + 1)
            body = segment[index + 1 : end].replace("\\", "\\\\")
            if body.startswith("!"):
                body = "^" + body[1:]
            result.append("[" + body + "]")
            index = end + 1
        else:
            result.append(re.escape(character))
            index += 1
    return "".join(result)


def resolve_repository_file(root: Path, value: str) -> Path:
    relative = normalize_repository_path(value)
    if any(segment.startswith("-") for segment in relative.parts):
        raise RepositoryPathError("repository file selector contains an option")
    try:
        resolved_root = root.resolve(strict=True)
        candidate = resolved_root.joinpath(*relative.parts).resolve(strict=True)
    except OSError as error:
        raise RepositoryPathError(f"repository file is unavailable: {value}") from error
    if not resolved_root.is_dir():
        raise RepositoryPathError(f"repository root is not a directory: {root}")
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise RepositoryPathError(
            f"repository file escapes its root: {value}"
        ) from error
    if not candidate.is_file():
        raise RepositoryPathError(f"repository path is not a file: {value}")
    return candidate
