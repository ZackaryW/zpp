from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.cli import app


class Environment:
    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.home = self.root / "home"
        self.marker = self.root / "executed"
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def bypass_state_command(self) -> list[str]:
        code = (
            "import os; "
            "print('child-bypass=' + str(bool(os.environ.get('_ZPP_BYPASS_TOKEN'))))"
        )
        return [sys.executable, "-c", code]

    def marker_command(self) -> list[str]:
        code = (
            "from pathlib import Path; "
            f"Path({str(self.marker)!r}).write_text('ran', encoding='utf-8')"
        )
        return [sys.executable, "-c", code]

    def governed_mutation_command(self) -> list[str]:
        target = self.root / "repository"
        target.mkdir()
        return [
            sys.executable,
            "-c",
            "from zpp.cli import app; app()",
            "--path",
            str(self.home),
            "lease",
            "acquire",
            "--root",
            str(target),
            "--change",
            "bypassed-change",
        ]

    def invoke_bypass(
        self, command: list[str], *, acknowledge: bool, reason: str = "owner approved"
    ):
        arguments = [
            "--path",
            str(self.home),
            "bypass",
            "--reason",
            reason,
        ]
        if acknowledge:
            arguments.append("--acknowledge")
        arguments.extend(("--", *command))
        return self.runner.invoke(app, arguments, catch_exceptions=False)

    def ordinary_bypass_state(self) -> bool:
        return bool(os.environ.get("_ZPP_BYPASS_TOKEN"))
