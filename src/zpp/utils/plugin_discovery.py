from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from zpp.utils.models import AgentName, ManagedStateError
from zpp.utils.processes import run_process


@dataclass(frozen=True, slots=True)
class ActivePlugin:
    agent: AgentName
    identity: str
    version: str
    root: Path


def discover_active_plugins(
    agent: AgentName,
    *,
    home: Path,
    target: Path,
) -> tuple[ActivePlugin, ...]:
    if agent == "codex":
        argv = ("codex", "plugin", "list", "--json")
    elif agent == "claude":
        argv = ("claude", "plugin", "list", "--json")
    else:
        argv = ("pi", "list", "--approve")

    try:
        result = run_process(argv, cwd=target)
    except OSError as error:
        raise ManagedStateError(f"cannot inspect active {agent} plugins: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise ManagedStateError(f"cannot inspect active {agent} plugins: {detail}")

    if agent == "codex":
        return parse_codex_plugin_list(result.stdout, home=home)
    if agent == "claude":
        return parse_claude_plugin_list(result.stdout)
    return parse_pi_plugin_list(result.stdout)


def parse_codex_plugin_list(
    payload: str,
    *,
    home: Path,
) -> tuple[ActivePlugin, ...]:
    value = _json(payload, "Codex")
    if not isinstance(value, dict) or not isinstance(value.get("installed"), list):
        raise ManagedStateError("Codex plugin listing has no installed array")

    plugins: list[ActivePlugin] = []
    for item in value["installed"]:
        record = _object(item, "Codex plugin entry")
        if record.get("installed") is not True or record.get("enabled") is not True:
            continue
        identity = _string(record, "pluginId", "Codex plugin entry")
        name = _path_segment(_string(record, "name", identity), "plugin name")
        marketplace = _path_segment(
            _string(record, "marketplaceName", identity),
            "marketplace name",
        )
        version = _path_segment(_string(record, "version", identity), "plugin version")
        root = home / ".codex" / "plugins" / "cache" / marketplace / name / version
        plugins.append(ActivePlugin("codex", identity, version, _installed_root(root, identity)))
    return _ordered_unique(plugins)


def parse_claude_plugin_list(payload: str) -> tuple[ActivePlugin, ...]:
    value = _json(payload, "Claude Code")
    if isinstance(value, dict):
        value = value.get("installed", value.get("plugins"))
    if not isinstance(value, list):
        raise ManagedStateError("Claude Code plugin listing is not an array")

    plugins: list[ActivePlugin] = []
    for item in value:
        record = _object(item, "Claude Code plugin entry")
        if record.get("enabled") is not True:
            continue
        identity = _first_string(record, ("id", "pluginId"), "Claude Code plugin identity")
        version = _string(record, "version", identity)
        installed_path = _first_string(
            record,
            ("installPath", "installedPath"),
            f"Claude Code plugin root for {identity}",
        )
        plugins.append(
            ActivePlugin(
                "claude",
                identity,
                version,
                _installed_root(Path(installed_path), identity),
            )
        )
    return _ordered_unique(plugins)


def parse_pi_plugin_list(output: str) -> tuple[ActivePlugin, ...]:
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    plugins: list[ActivePlugin] = []
    position = 0
    while position < len(lines):
        line = lines[position]
        if not line.startswith(" ") and line.endswith(" packages:"):
            position += 1
            continue
        if not line.startswith("  ") or line.startswith("    "):
            raise ManagedStateError(f"Pi plugin listing is malformed near {line!r}")
        if position + 1 >= len(lines) or not lines[position + 1].startswith("    "):
            raise ManagedStateError(f"Pi plugin listing has no root for {line.strip()!r}")

        source = line.strip()
        root = Path(lines[position + 1].strip())
        identity, version = _pi_identity_version(source, root)
        plugins.append(
            ActivePlugin("pi", identity, version, _installed_root(root, identity))
        )
        position += 2
    return _ordered_unique(plugins)


def _json(payload: str, owner: str) -> Any:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as error:
        raise ManagedStateError(f"{owner} plugin listing is not valid JSON") from error


def _object(value: object, subject: str) -> dict[str, Any]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ManagedStateError(f"{subject} is not an object")
    return value


def _string(record: dict[str, Any], key: str, subject: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ManagedStateError(f"{subject} has no valid {key}")
    return value


def _first_string(
    record: dict[str, Any],
    keys: tuple[str, ...],
    subject: str,
) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    raise ManagedStateError(f"{subject} is missing")


def _path_segment(value: str, subject: str) -> str:
    if value in {".", ".."} or Path(value).name != value or "/" in value or "\\" in value:
        raise ManagedStateError(f"invalid {subject}: {value!r}")
    return value


def _installed_root(root: Path, identity: str) -> Path:
    try:
        resolved = root.resolve(strict=True)
    except OSError as error:
        raise ManagedStateError(f"active plugin {identity!r} has no installed root: {root}") from error
    if not resolved.is_dir():
        raise ManagedStateError(f"active plugin {identity!r} root is not a directory: {root}")
    return resolved


def _ordered_unique(plugins: list[ActivePlugin]) -> tuple[ActivePlugin, ...]:
    ordered = sorted(plugins, key=lambda plugin: plugin.identity)
    for first, second in zip(ordered, ordered[1:], strict=False):
        if first.identity == second.identity:
            raise ManagedStateError(f"duplicate active plugin identity: {first.identity}")
    return tuple(ordered)


def _pi_identity_version(source: str, root: Path) -> tuple[str, str]:
    if source.startswith("npm:"):
        package = source.removeprefix("npm:")
        marker = package.rfind("@")
        if marker > 0:
            return f"npm:{package[:marker]}", package[marker + 1 :]
        return f"npm:{package}", "unversioned"
    if source.startswith("git:") or source.startswith(("https://", "http://", "ssh://", "git://")):
        marker = source.rfind("@")
        separator = max(source.rfind("/"), source.rfind(":"))
        if marker > separator:
            return source[:marker], source[marker + 1 :]
        return source, "unversioned"
    if source.startswith((".", "/", "~")) or Path(source).is_absolute():
        return f"local:{root.resolve(strict=False)}", "local"
    return f"package:{source}", "unversioned"
