from __future__ import annotations

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner


def before_scenario(context, scenario) -> None:
    context.temporary = tempfile.TemporaryDirectory(prefix="zpp-behave-")
    context.sandbox = Path(context.temporary.name)
    context.home = context.sandbox / "home"
    context.project = context.sandbox / "project"
    context.home.mkdir()
    context.project.mkdir()
    context.original_cwd = Path.cwd()
    os.chdir(context.project)

    context.runner = CliRunner()
    context.results = []
    context.interactive = False
    context.selector_answer = ()
    context.selector_offers = []
    context.env = {
        "HOME": str(context.home),
        "USERPROFILE": str(context.home),
        "ZPP_PROFILE": None,
        "PATH": os.environ.get("PATH", ""),
        "NO_COLOR": "1",
    }
    context.paths = {
        "c:\\work\\a": context.sandbox / "work" / "a",
        "c:\\work\\b": context.sandbox / "work" / "b",
        "c:/work/b": context.sandbox / "work" / "b",
        "c:\\work\\keep": context.sandbox / "work" / "keep",
        "c:\\missing": context.sandbox / "missing",
        "c:\\work\\file.txt": context.sandbox / "work" / "file.txt",
        "c:\\outside": context.sandbox / "outside",
    }


def after_scenario(context, scenario) -> None:
    os.chdir(context.original_cwd)
    context.temporary.cleanup()
