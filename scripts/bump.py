#!/usr/bin/env python
"""Bump zpp and zpp-mcp in lockstep, then re-lock the workspace.

Both packages share one version: zpp-mcp depends on zpp and they release
together, so a single bump moves the whole workspace. Driven by uv
(`uv version`), so it stays consistent with the uv dev environment.

Usage:
    uv run python scripts/bump.py [patch|minor|major]   # default: patch

Wire it through .vscode/tasks.json ("uv: bump version").
"""

import subprocess
import sys

PARTS = {"major", "minor", "patch", "stable", "alpha", "beta", "rc", "post", "dev"}
MEMBER = "zpp-mcp"


def uv(*args: str) -> str:
    proc = subprocess.run(["uv", *args], text=True, capture_output=True)
    if proc.returncode != 0:
        sys.exit(proc.stderr.strip() or proc.stdout.strip() or "uv failed")
    return proc.stdout.strip()


def main() -> None:
    part = sys.argv[1] if len(sys.argv) > 1 else "patch"
    if part not in PARTS:
        sys.exit(f"unknown bump part '{part}' (choose: {', '.join(sorted(PARTS))})")

    # --frozen edits pyproject without re-locking; we re-lock once at the end.
    new = uv("version", "--bump", part, "--frozen", "--short")   # bumps root zpp
    uv("version", new, "--package", MEMBER, "--frozen")          # member lockstep
    uv("lock")                                                   # single re-lock
    print(f"bumped zpp + {MEMBER} -> {new}")


if __name__ == "__main__":
    main()
