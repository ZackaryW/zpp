"""saucepan adapter: the only module that talks to the saucepan CLI.

Managed mode (default): the release binary is fetched to ~/.zpp/bin/saucepan
on first use and invoked from there. System mode: saucepan must be on PATH;
zpp never installs it. The pack contract: saucepan runs with cwd
~/.zpp/saucepan and populates pack dirs there (this adapter is the seam if
upstream's layout differs)."""

import os
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path

from ..utils.paths import zpp_home

RELEASE_URL_ENV = "ZPP_SAUCEPAN_URL"
# saucepan publishes release assets under Rust target triples, not
# {os}-{arch}. macOS: one universal binary covers both arches (no arch-token
# to mismatch); Windows: per-arch msvc build with a .exe suffix; Linux: no
# asset is published, so managed mode cannot resolve one. See
# github.com/ZackaryW/saucepan/releases.
RELEASE_BASE = "https://github.com/ZackaryW/saucepan/releases/latest/download"


class SauceError(RuntimeError):
    pass


def managed_binary() -> Path:
    return zpp_home() / "bin" / "saucepan"


def _asset_name(system: str, machine: str) -> str:
    """The release asset for a platform, matching saucepan's published names."""
    if system == "darwin":
        return "saucepan-universal-apple-darwin"
    if system == "windows":
        arch = "aarch64" if machine in ("arm64", "aarch64") else "x86_64"
        return f"saucepan-{arch}-pc-windows-msvc.exe"
    raise SauceError(
        f"no managed saucepan binary is published for {system}-{machine}; "
        'install saucepan and set [traits] saucepan = "system", or set '
        f"{RELEASE_URL_ENV} to a binary URL"
    )


def _release_url() -> str:
    override = os.environ.get(RELEASE_URL_ENV)
    if override:
        return override
    return f"{RELEASE_BASE}/{_asset_name(platform.system().lower(), platform.machine().lower())}"


def ensure_binary(mode: str) -> tuple[Path, bool]:
    """Resolve the saucepan binary per mode. Returns (path, fetched_now)."""
    if mode == "system":
        found = shutil.which("saucepan")
        if not found:
            raise SauceError(
                "saucepan not found on PATH (mode is 'system'; install it, "
                "or set [traits] saucepan = \"managed\")"
            )
        return Path(found), False
    binary = managed_binary()
    if binary.is_file():
        return binary, False
    binary.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(_release_url()) as response:
            binary.write_bytes(response.read())
    except OSError as e:
        raise SauceError(f"failed to fetch saucepan release: {e}")
    binary.chmod(0o755)
    return binary, True


def install(binary: Path, ref: str) -> None:
    """Install/update a pack; packs land under ~/.zpp/saucepan/."""
    workdir = zpp_home() / "saucepan"
    workdir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(binary), "install", ref], capture_output=True, text=True, cwd=workdir
    )
    if proc.returncode != 0:
        raise SauceError(
            f"saucepan install {ref} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
