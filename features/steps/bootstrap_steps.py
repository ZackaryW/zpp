from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace

from behave import given, then, when


@given("a clean user home and a project without local ZPP state")
def given_clean_user_home(context: object) -> None:
    workspace = tempfile.TemporaryDirectory()
    context.add_cleanup(workspace.cleanup)

    root = Path(workspace.name)
    context.user_home = root / "home"
    context.project = root / "project"
    context.user_home.mkdir()
    context.project.mkdir()


@when("the user runs zpp init")
def when_user_runs_zpp_init(context: object) -> None:
    environment = os.environ.copy()
    environment["HOME"] = str(context.user_home)
    environment["USERPROFILE"] = str(context.user_home)

    executable = shutil.which("zpp", path=environment.get("PATH"))
    if executable is None:
        context.result = SimpleNamespace(
            returncode=127,
            stdout="",
            stderr="zpp executable was not found on PATH",
        )
        return

    context.result = subprocess.run(
        [executable, "init"],
        cwd=context.project,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@then("initialization succeeds")
def then_initialization_succeeds(context: object) -> None:
    assert context.result.returncode == 0, (
        f"zpp init exited with {context.result.returncode}\n"
        f"stdout:\n{context.result.stdout}\n"
        f"stderr:\n{context.result.stderr}"
    )


@then("the global trait trigger configuration exists")
def then_global_trait_trigger_exists(context: object) -> None:
    assert (context.user_home / ".zpp" / "global" / "trait.json").is_file()


@then("the project still has no local ZPP state")
def then_project_has_no_local_zpp_state(context: object) -> None:
    assert not (context.project / ".zpp").exists()
