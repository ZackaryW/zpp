"""Capability-local verification subjects for trait resolution.

The selection-policy case matrix lives in `tests/unit/test_resolution.py`.
These subjects drive the public `zpp resolve` boundary instead, proving that
the resolved bodies, activation filtering, and diagnostics reach a caller.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.cli import app

AUTOMATIC_DOCUMENT = (
    "[meta]\nselection='first-win'\n"
    "[[trait]]\n[trait.facet]\nlanguage='python'\n"
    "[trait.content]\nbody='automatic policy'\n"
)

MANUAL_DOCUMENT = (
    "[meta]\nselection='all'\nactivation='manual'\n"
    "[[trait]]\n[trait.facet]\nlanguage='python'\n"
    "[trait.content]\nbody='manual policy'\n"
)


class Workspace:
    """A disposable repository carrying explicit trait documents."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.root = Path(self._temporary.name)
        (self.root / "pyproject.toml").write_text(
            "[project]\nname='example'\ndependencies=['click']\n", encoding="utf-8"
        )
        self.traits = self.root / ".zpp" / "traits"
        self.traits.mkdir(parents=True)
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def write_trait(self, family: str, document: str) -> None:
        (self.traits / f"{family}.toml").write_text(document, encoding="utf-8")

    def resolve(self, *arguments: str):
        return self.runner.invoke(app, ["resolve", str(self.root), *arguments])
