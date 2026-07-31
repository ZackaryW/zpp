from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Mapping, Sequence

from zpp.utils.codespace_models import CodespaceClaim
from zpp.utils.openspec_adapter import register_private_store


def private_openspec_environment(
    codespace_root: Path,
    base: Mapping[str, str],
) -> dict[str, str]:
    environment = dict(base)
    environment["XDG_DATA_HOME"] = str(
        (codespace_root / "openspec-data").resolve()
    )
    return environment


def materialize_private_registry(
    claim: CodespaceClaim,
    *,
    environment: Mapping[str, str],
) -> None:
    for member in claim.members:
        if member.kind == "store" and member.store_id is not None:
            register_private_store(
                member.store_id,
                member.effective_path,
                env=environment,
            )


def execute_codespace_command(
    argv: Sequence[str],
    *,
    environment: Mapping[str, str],
    cwd: Path,
) -> int:
    completed = subprocess.run(
        tuple(argv),
        cwd=cwd,
        env=dict(environment),
        check=False,
    )
    return completed.returncode


def activate_codespace_shell(
    *,
    environment: Mapping[str, str],
    cwd: Path,
) -> int:
    shell = environment.get("COMSPEC") or environment.get("SHELL")
    if not shell:
        raise ValueError("no shell is configured in the codespace environment")
    completed = subprocess.run(
        (shell,),
        cwd=cwd,
        env=dict(environment),
        check=False,
    )
    return completed.returncode
