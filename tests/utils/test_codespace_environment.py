from pathlib import Path

import pytest

from zpp.utils.codespace_environment import (
    activate_codespace_shell,
    execute_codespace_command,
    materialize_private_registry,
    private_openspec_environment,
)
from zpp.utils.codespace_models import CodespaceClaim, CodespaceMember


def _claim(tmp_path: Path) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        members=(
            CodespaceMember(
                name="store",
                original_path=tmp_path / "store",
                effective_path=tmp_path / "store-instance",
                checkout_key="store-key",
                commit="abc",
                kind="store",
                store_id="original-id",
                generated_worktree=True,
                branch="zpp/instance/0",
            ),
            CodespaceMember(
                name="project",
                original_path=tmp_path / "project",
                effective_path=tmp_path / "project",
                checkout_key="project-key",
                commit="def",
                kind="project",
            ),
        ),
    )


def test_private_environment_preserves_base_and_registers_original_store_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment = private_openspec_environment(
        tmp_path / "codespace",
        {"KEEP": "yes", "XDG_DATA_HOME": "global"},
    )
    calls: list[tuple[str, Path, dict[str, str]]] = []
    monkeypatch.setattr(
        "zpp.utils.codespace_environment.register_private_store",
        lambda store_id, root, *, env: calls.append((store_id, root, dict(env))),
    )

    materialize_private_registry(_claim(tmp_path), environment=environment)

    assert environment["KEEP"] == "yes"
    assert environment["XDG_DATA_HOME"] == str(
        (tmp_path / "codespace" / "openspec-data").resolve()
    )
    assert [(store_id, root) for store_id, root, _ in calls] == [
        ("original-id", tmp_path / "store-instance")
    ]


def test_codespace_command_and_shell_propagate_exit_codes_and_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    class Completed:
        returncode = 9

    def fake_run(argv, **kwargs):
        calls.append((tuple(argv), kwargs))
        return Completed()

    monkeypatch.setattr("zpp.utils.codespace_environment.subprocess.run", fake_run)
    environment = {"COMSPEC": "custom-shell", "KEEP": "yes"}

    assert execute_codespace_command(
        ("openspec", "context", "--json"),
        environment=environment,
        cwd=tmp_path,
    ) == 9
    assert activate_codespace_shell(environment=environment, cwd=tmp_path) == 9
    assert calls[0][0] == ("openspec", "context", "--json")
    assert calls[1][0] == ("custom-shell",)
    assert all(call[1]["env"] == environment for call in calls)
