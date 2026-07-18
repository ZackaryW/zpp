"""One table of governance tools consumed by both doctor (detect-only) and
bootstrap (idempotent install), so they can never disagree. Ported from
governance-of-agents-1 scripts/setup.sh and pv-doctor. uv is the sole
prerequisite zpp may assume."""

import platform
import shutil
import subprocess
from pathlib import Path

# (command, darwin install, fallback install-or-None-for-manual, manual hint)
TOOLS: list[dict] = [
    {"cmd": "node", "darwin": ["brew", "install", "node"], "fallback": None,
     "hint": "install Node.js >= 20.19 via your package manager or nvm"},
    {"cmd": "jq", "darwin": ["brew", "install", "jq"], "fallback": None,
     "hint": "install jq via your package manager"},
    {"cmd": "rg", "darwin": ["brew", "install", "ripgrep"], "fallback": None,
     "hint": "install ripgrep via your package manager"},
    {"cmd": "zmem",
     "darwin": ["uv", "tool", "install", "git+https://github.com/ZackaryW/zmem.git"],
     "fallback": ["uv", "tool", "install", "git+https://github.com/ZackaryW/zmem.git"],
     "hint": "uv tool install git+https://github.com/ZackaryW/zmem.git"},
    {"cmd": "codegraph", "darwin": None, "fallback": None,
     "hint": "curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh"},
    {"cmd": "openspec", "darwin": ["npm", "install", "-g", "@fission-ai/openspec"],
     "fallback": ["npm", "install", "-g", "@fission-ai/openspec"],
     "hint": "npm install -g @fission-ai/openspec"},
    {"cmd": "saucepan", "managed": True, "darwin": None, "fallback": None,
     "hint": "release binary; managed mode fetches it to ~/.zpp/bin on first use"},
]


def _saucepan_mode() -> str:
    from . import governance

    try:
        return (governance.resolve_config(Path("."))["effective"]
                .get("traits", {}).get("saucepan", "managed"))
    except Exception:
        return "managed"


def _managed_present(tool: dict) -> tuple[bool, str | None]:
    """(present, provenance) for a managed-mode-capable tool."""
    from . import sauce

    mode = _saucepan_mode()
    managed = sauce.managed_binary()
    if managed.is_file():
        return True, f"managed ({managed})"
    if shutil.which(tool["cmd"]):
        return True, f"{mode} (PATH)"
    return False, None


def _version(cmd: str) -> str:
    try:
        proc = subprocess.run([cmd, "--version"], capture_output=True, text=True,
                              timeout=10)
        return proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    except Exception:
        return ""


def doctor() -> list[dict]:
    """Detect-only: one entry per tool, never mutates."""
    report = []
    for tool in TOOLS:
        if tool.get("managed"):
            present, provenance = _managed_present(tool)
            report.append({
                "tool": tool["cmd"], "present": present,
                "version": provenance,
                "hint": None if present else tool["hint"],
            })
            continue
        present = shutil.which(tool["cmd"]) is not None
        report.append({
            "tool": tool["cmd"],
            "present": present,
            "version": _version(tool["cmd"]) if present else None,
            "hint": None if present else tool["hint"],
        })
    return report


def bootstrap(dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Install missing tools; returns (installed, manual-steps-remaining)."""
    installed, manual = [], []
    is_darwin = platform.system() == "Darwin"
    for tool in TOOLS:
        if tool.get("managed"):
            if _managed_present(tool)[0]:
                continue
            if _saucepan_mode() == "system":
                manual.append(f"{tool['cmd']}: {tool['hint']}")
                continue
            if dry_run:
                installed.append(f"{tool['cmd']}: would fetch release binary to ~/.zpp/bin")
                continue
            from . import sauce

            try:
                binary, _ = sauce.ensure_binary("managed")
                installed.append(f"{tool['cmd']} ({binary})")
            except sauce.SauceError as e:
                manual.append(f"{tool['cmd']}: {e}")
            continue
        if shutil.which(tool["cmd"]):
            continue
        strategy = tool["darwin"] if is_darwin else tool["fallback"]
        if strategy is None:
            manual.append(f"{tool['cmd']}: {tool['hint']}")
            continue
        if dry_run:
            installed.append(f"{tool['cmd']}: would run {' '.join(strategy)}")
            continue
        proc = subprocess.run(strategy)
        if proc.returncode == 0 and shutil.which(tool["cmd"]):
            installed.append(tool["cmd"])
        else:
            manual.append(f"{tool['cmd']}: {tool['hint']}")
    return installed, manual
