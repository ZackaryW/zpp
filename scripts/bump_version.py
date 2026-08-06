# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Synchronize ZPP's authored release declarations and regenerate uv.lock."""

from __future__ import annotations

import argparse
from collections.abc import Callable
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


STABLE_VERSION = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\Z")
PROJECT_HEADER = re.compile(r"(?m)^[ \t]*\[project\][ \t]*(?:#.*)?\r?$")
TABLE_HEADER = re.compile(r"(?m)^[ \t]*\[{1,2}[^\]\r\n]+\]{1,2}[ \t]*(?:#.*)?\r?$")
PROJECT_VERSION = re.compile(
    r"(?m)^(?P<prefix>[ \t]*version[ \t]*=[ \t]*)"
    r"(?P<quote>['\"])(?P<value>[^'\"\r\n]+)(?P=quote)"
    r"(?P<suffix>[ \t]*(?:#.*)?)(?P<cr>\r?)$"
)
RUNTIME_VERSION = re.compile(
    r"(?m)^(?P<prefix>[ \t]*__version__[ \t]*=[ \t]*)"
    r"(?P<quote>['\"])(?P<value>[^'\"\r\n]+)(?P=quote)"
    r"(?P<suffix>[ \t]*(?:#.*)?)(?P<cr>\r?)$"
)


class VersionBumpError(ValueError):
    """The repository cannot be versioned without an ambiguous rewrite."""


def _replace_match(text: str, match: re.Match[str], target: str) -> str:
    replacement = (
        f"{match.group('prefix')}{match.group('quote')}{target}"
        f"{match.group('quote')}{match.group('suffix')}{match.group('cr')}"
    )
    return text[: match.start()] + replacement + text[match.end() :]


def _replace_project_version(text: str, target: str) -> str:
    headers = list(PROJECT_HEADER.finditer(text))
    if len(headers) != 1:
        raise VersionBumpError("pyproject.toml must contain exactly one [project] section")
    header = headers[0]
    next_header = TABLE_HEADER.search(text, header.end())
    section_end = next_header.start() if next_header else len(text)
    section = text[header.end() : section_end]
    declarations = list(PROJECT_VERSION.finditer(section))
    if len(declarations) != 1:
        raise VersionBumpError(
            "the [project] section must contain exactly one string version declaration"
        )
    declaration = declarations[0]
    absolute_start = header.end() + declaration.start()
    absolute_end = header.end() + declaration.end()
    absolute = PROJECT_VERSION.match(text, absolute_start, absolute_end)
    assert absolute is not None
    return _replace_match(text, absolute, target)


def _replace_runtime_version(text: str, target: str) -> str:
    declarations = list(RUNTIME_VERSION.finditer(text))
    if len(declarations) != 1:
        raise VersionBumpError(
            "src/zpp/__init__.py must contain exactly one string __version__ declaration"
        )
    return _replace_match(text, declarations[0], target)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _run_uv_lock(root: Path) -> None:
    subprocess.run(["uv", "lock"], cwd=root, check=True)


def bump_version(
    project_root: Path,
    target: str,
    *,
    run_lock: Callable[[Path], None] = _run_uv_lock,
) -> None:
    """Synchronize the project/runtime version and regenerate the uv lockfile."""
    if STABLE_VERSION.fullmatch(target) is None:
        raise VersionBumpError("target version must use stable X.Y.Z form")

    root = project_root.resolve()
    project_file = root / "pyproject.toml"
    runtime_file = root / "src" / "zpp" / "__init__.py"
    lock_file = root / "uv.lock"
    owned = (project_file, runtime_file, lock_file)

    try:
        project_bytes = project_file.read_bytes()
        runtime_bytes = runtime_file.read_bytes()
        project_text = project_bytes.decode("utf-8")
        runtime_text = runtime_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise VersionBumpError(f"cannot read authored version declarations: {error}") from error

    updated_project = _replace_project_version(project_text, target).encode("utf-8")
    updated_runtime = _replace_runtime_version(runtime_text, target).encode("utf-8")
    snapshots = {path: path.read_bytes() if path.exists() else None for path in owned}

    try:
        _atomic_write(project_file, updated_project)
        _atomic_write(runtime_file, updated_runtime)
        run_lock(root)
    except BaseException as error:
        try:
            for path, content in snapshots.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    _atomic_write(path, content)
        except BaseException as restore_error:
            raise VersionBumpError(
                f"version update failed and repository restoration also failed: {restore_error}"
            ) from error
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize ZPP release declarations and regenerate uv.lock."
    )
    parser.add_argument("version", help="stable release in X.Y.Z form")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        bump_version(root, args.version)
    except (VersionBumpError, OSError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Synchronized ZPP version {args.version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
