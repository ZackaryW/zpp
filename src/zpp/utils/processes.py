from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner(Protocol):
    def run(self, argv: Sequence[str], *, cwd: Path) -> ProcessResult: ...


class SubprocessRunner:
    def run(self, argv: Sequence[str], *, cwd: Path) -> ProcessResult:
        completed = subprocess.run(
            tuple(argv),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return ProcessResult(
            tuple(argv), completed.returncode, completed.stdout, completed.stderr
        )
