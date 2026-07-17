"""~/.zpp layout. ZPP_HOME overrides for tests."""

import os
from pathlib import Path


def zpp_home() -> Path:
    return Path(os.environ.get("ZPP_HOME", Path.home() / ".zpp"))


def worksets_dir() -> Path:
    return zpp_home() / "worksets"


def sidecar_path(name: str) -> Path:
    return worksets_dir() / f"{name}.toml"


def snapshots_dir(name: str) -> Path:
    return worksets_dir() / name / "snapshots"
