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
DEFAULT_RELEASE_URL = (
    "https://github.com/ZackaryW/saucepan/releases/latest/download/saucepan-{os}-{arch}"
)


class SauceError(RuntimeError):
    pass


def managed_binary() -> Path:
    return zpp_home() / "bin" / "saucepan"


def _release_url() -> str:
    return os.environ.get(RELEASE_URL_ENV) or DEFAULT_RELEASE_URL.format(
        os=platform.system().lower(), arch=platform.machine().lower()
    )


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
