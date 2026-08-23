"""Capability-local verification subjects for packaged workflow provisioning."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from typer.testing import CliRunner

from zpp.artifacts import (
    OPENSPEC_ADAPTER_SKILL_NAMES,
    REPOSITORY_EVIDENCE_SKILL_NAME,
    WORKFLOW_SKILL_NAMES,
    packaged_companion_skills,
    packaged_workflow_skills,
)
from zpp.cli import app
from zpp.cli.lifecycle import OBSOLETE_WORKFLOW_SKILL_NAMES

CODEX_SKILLS = Path(".codex/skills")
REPOSITORY_ROOT = Path(__file__).parents[2]


def _run(
    arguments: tuple[str, ...],
    *,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    failure = (
        f"command failed: {arguments!r}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert result.returncode == 0, failure
    return result


def _tool_python(tool_directory: Path) -> Path:
    if os.name == "nt":
        return tool_directory / "zpp" / "Scripts" / "python.exe"
    return tool_directory / "zpp" / "bin" / "python"


def _tool_command(bin_directory: Path) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return bin_directory / f"zpp{suffix}"


def _wheel_version(wheel: Path) -> str:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = archive.read(metadata_name).decode("utf-8")
    for line in metadata.splitlines():
        if line.startswith("Version: "):
            return line.removeprefix("Version: ")
    raise AssertionError(f"built wheel has no Version metadata: {wheel}")


@dataclass(frozen=True)
class DistributionEvidence:
    """Observed public results from one isolated uv tool installation."""

    wheel_version: str
    project_version: str
    module_version: str
    cli_output: str
    tool_list: str
    command_names: tuple[str, ...]
    installed_packages: frozenset[str]
    bundler_console_commands: tuple[str, ...]


class ToolEnvironment:
    """A disposable uv tool destination that never touches the user tool home."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.tool_directory = self.root / "tools"
        self.bin_directory = self.root / "bin"
        self.distribution_directory = self.root / "dist"
        self.environment = os.environ.copy()
        self.environment.update(
            {
                "UV_TOOL_DIR": str(self.tool_directory),
                "UV_TOOL_BIN_DIR": str(self.bin_directory),
                "UV_NO_PROGRESS": "1",
            }
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def install(self) -> DistributionEvidence:
        _run(
            (
                "uv",
                "build",
                "--wheel",
                "--out-dir",
                str(self.distribution_directory),
            ),
            environment=self.environment,
        )
        wheels = tuple(self.distribution_directory.glob("zpp-*.whl"))
        assert len(wheels) == 1, wheels
        wheel = wheels[0]

        _run(
            (
                "uv",
                "tool",
                "install",
                "--python",
                sys.executable,
                "--force",
                str(wheel),
            ),
            environment=self.environment,
        )
        tool_list = _run(("uv", "tool", "list"), environment=self.environment).stdout

        command = _tool_command(self.bin_directory)
        assert command.is_file(), command
        cli_output = _run((str(command), "--version"), environment=self.environment)
        python = _tool_python(self.tool_directory)
        module_version = _run(
            (str(python), "-c", "import zpp; print(zpp.__version__)"),
            environment=self.environment,
        ).stdout.strip()
        bundler_console_commands = tuple(
            filter(
                None,
                _run(
                    (
                        str(python),
                        "-c",
                        "from importlib.metadata import distribution; "
                        "print('\\n'.join(ep.name for ep in "
                        "distribution('openspec-bundler').entry_points "
                        "if ep.group == 'console_scripts'))",
                    ),
                    environment=self.environment,
                ).stdout.splitlines(),
            )
        )
        installed = json.loads(
            _run(
                ("uv", "pip", "list", "--python", str(python), "--format", "json"),
                environment=self.environment,
            ).stdout
        )
        project = tomllib.loads(
            (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]

        command_names = tuple(
            sorted(
                path.name.removesuffix(".exe")
                for path in self.bin_directory.iterdir()
                if path.is_file()
            )
        )
        return DistributionEvidence(
            wheel_version=_wheel_version(wheel),
            project_version=project["version"],
            module_version=module_version,
            cli_output=cli_output.stdout.strip(),
            tool_list=tool_list,
            command_names=command_names,
            installed_packages=frozenset(item["name"] for item in installed),
            bundler_console_commands=bundler_console_commands,
        )


def packaged_skill_names() -> tuple[str, ...]:
    return tuple(
        skill.name
        for skill in (*packaged_workflow_skills(), *packaged_companion_skills())
    )


def workflow_names() -> tuple[str, ...]:
    return tuple(skill.name for skill in packaged_workflow_skills())


def expected_asset_count() -> int:
    return len(packaged_skill_names()) + 1


class Home:
    """A disposable user home with an isolated ZPP product home."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        root = Path(self._temporary.name)
        self.user_home = root / "user"
        self.user_home.mkdir(parents=True, exist_ok=True)
        self.product_home = root / "zpp-home"
        self._patch = patch.object(
            Path, "home", classmethod(lambda cls: self.user_home)
        )
        self._patch.start()
        self.runner = CliRunner()

    def close(self) -> None:
        self._patch.stop()
        self._temporary.cleanup()

    def run(self, *arguments: str):
        return self.runner.invoke(app, list(arguments))

    def run_json(self, *arguments: str):
        result = self.run(*arguments)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def skill_path(self, name: str) -> Path:
        return self.user_home / CODEX_SKILLS / name


__all__ = [
    "OBSOLETE_WORKFLOW_SKILL_NAMES",
    "OPENSPEC_ADAPTER_SKILL_NAMES",
    "REPOSITORY_EVIDENCE_SKILL_NAME",
    "WORKFLOW_SKILL_NAMES",
    "DistributionEvidence",
    "Home",
    "ToolEnvironment",
    "expected_asset_count",
    "packaged_skill_names",
    "workflow_names",
]
