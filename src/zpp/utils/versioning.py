from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import re

from zpp.utils.json_io import atomic_write_bytes
from zpp.utils.processes import run_process


LockRefresher = Callable[[Path], None]

_STABLE_VERSION = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
)
_SECTION = re.compile(r"(?m)^\s*\[[^]\r\n]+\]\s*(?:\r?\n|$)")
_PROJECT = re.compile(r"(?m)^\s*\[project\]\s*(?:\r?\n|$)")
_PROJECT_VERSION = re.compile(
    r"(?m)^(?P<prefix>\s*version\s*=\s*)(?P<quote>['\"])(?P<value>[^'\"\r\n]+)(?P=quote)(?P<suffix>\s*(?:#.*)?)$"
)
_RUNTIME_VERSION = re.compile(
    r"(?m)^(?P<prefix>\s*__version__\s*=\s*)(?P<quote>['\"])(?P<value>[^'\"\r\n]+)(?P=quote)(?P<suffix>\s*(?:#.*)?)$"
)


@dataclass(frozen=True, slots=True)
class VersionSyncResult:
    project_version: str
    runtime_version: str
    target_version: str
    changed: bool


def synchronize_version(
    root: Path,
    target: str,
    *,
    run_lock: LockRefresher | None = None,
) -> VersionSyncResult:
    if _STABLE_VERSION.fullmatch(target) is None:
        raise ValueError("version must use stable X.Y.Z syntax")

    project_root = root.resolve()
    pyproject = project_root / "pyproject.toml"
    initializer = project_root / "src" / "zpp" / "__init__.py"
    lockfile = project_root / "uv.lock"
    originals = {
        pyproject: _required_bytes(pyproject),
        initializer: _required_bytes(initializer),
        lockfile: lockfile.read_bytes() if lockfile.is_file() else None,
    }

    project_text = _decode(pyproject, originals[pyproject])
    runtime_text = _decode(initializer, originals[initializer])
    project_version, updated_project = _replace_project_version(project_text, target)
    runtime_version, updated_runtime = _replace_unique(
        runtime_text,
        _RUNTIME_VERSION,
        target,
        "exactly one __version__ assignment",
    )

    try:
        project_bytes = updated_project.encode("utf-8")
        runtime_bytes = updated_runtime.encode("utf-8")
        if project_bytes != originals[pyproject]:
            atomic_write_bytes(pyproject, project_bytes)
        if runtime_bytes != originals[initializer]:
            atomic_write_bytes(initializer, runtime_bytes)
        (run_lock or refresh_uv_lock)(project_root)
    except BaseException:
        _restore(originals)
        raise

    changed = any(
        _optional_bytes(path) != original for path, original in originals.items()
    )
    return VersionSyncResult(
        project_version,
        runtime_version,
        target,
        changed,
    )


def refresh_uv_lock(root: Path) -> None:
    result = run_process(("uv", "lock"), cwd=root)
    if result.returncode != 0:
        diagnostic = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"uv lock failed: {diagnostic}")


def _replace_project_version(text: str, target: str) -> tuple[str, str]:
    project_sections = list(_PROJECT.finditer(text))
    if len(project_sections) != 1:
        raise ValueError("pyproject.toml must contain exactly one [project] section")
    start = project_sections[0].end()
    next_section = _SECTION.search(text, start)
    end = next_section.start() if next_section is not None else len(text)
    fragment = text[start:end]
    previous, replacement = _replace_unique(
        fragment,
        _PROJECT_VERSION,
        target,
        "exactly one [project] version assignment",
    )
    return previous, f"{text[:start]}{replacement}{text[end:]}"


def _replace_unique(
    text: str,
    pattern: re.Pattern[str],
    target: str,
    expectation: str,
) -> tuple[str, str]:
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"source must contain {expectation}")
    match = matches[0]
    replacement = (
        f"{match.group('prefix')}{match.group('quote')}{target}"
        f"{match.group('quote')}{match.group('suffix')}"
    )
    return match.group("value"), f"{text[:match.start()]}{replacement}{text[match.end():]}"


def _decode(path: Path, content: bytes | None) -> str:
    assert content is not None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"version source is not UTF-8: {path}") from error


def _required_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError(f"required version source is missing: {path}")
    return path.read_bytes()


def _optional_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def _restore(originals: dict[Path, bytes | None]) -> None:
    for path, content in originals.items():
        if content is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write_bytes(path, content)
