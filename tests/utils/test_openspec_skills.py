from pathlib import Path

import pytest

from zpp.utils.models import ManagedStateError
from zpp.utils.openspec_skills import (
    OPENSPEC_CORE_SKILL_NAMES,
    detect_openspec_version,
    generate_openspec_skill_bundles,
)
from zpp.utils.processes import ProcessResult


def test_generation_collects_exact_agent_bytes_and_cleans_temporary_project(
    tmp_path: Path,
) -> None:
    calls: list[tuple[tuple[str, ...], Path | None, dict[str, str] | None]] = []

    def run(argv, *, cwd=None, env=None):
        arguments = tuple(argv)
        calls.append((arguments, cwd, None if env is None else dict(env)))
        if arguments == ("openspec", "--version"):
            return ProcessResult(arguments, 0, "1.7.0\n", "")
        assert cwd is not None
        roots = {
            "codex": cwd / ".codex" / "skills",
            "pi": cwd / ".pi" / "skills",
            "claude": cwd / ".claude" / "skills",
        }
        for agent, root in roots.items():
            for name in OPENSPEC_CORE_SKILL_NAMES:
                skill = root / name
                skill.mkdir(parents=True, exist_ok=True)
                (skill / "SKILL.md").write_bytes(f"{agent}:{name}\n".encode())
        return ProcessResult(arguments, 0, "initialized\n", "")

    bundles = generate_openspec_skill_bundles(
        ("codex", "pi", "claude"),
        detected_version="1.7.0",
        temporary_parent=tmp_path,
        run=run,
    )

    assert tuple(bundle.agent for bundle in bundles) == ("codex", "pi", "claude")
    assert all(bundle.version == "1.7.0" for bundle in bundles)
    assert all(
        {file.relative_path.split("/", 1)[0] for file in bundle.files}
        == set(OPENSPEC_CORE_SKILL_NAMES)
        for bundle in bundles
    )
    assert next(file.content for file in bundles[0].files if file.relative_path.endswith("SKILL.md")).startswith(b"codex:")
    assert len(calls) == 1
    assert calls[0][0] == (
        "openspec",
        "init",
        ".",
        "--tools",
        "codex,pi,claude",
        "--force",
    )
    assert calls[0][2] is not None
    data_root = Path(calls[0][2]["XDG_DATA_HOME"])
    assert data_root.is_relative_to(tmp_path)
    assert not data_root.exists()
    assert list(tmp_path.iterdir()) == []


def test_version_detection_falls_back_to_none_and_generation_failure_cleans(
    tmp_path: Path,
) -> None:
    def unavailable_version(argv, *, cwd=None, env=None):
        del cwd, env
        arguments = tuple(argv)
        return ProcessResult(arguments, 1, "", "missing")

    assert detect_openspec_version(unavailable_version) is None

    def failing_generation(argv, *, cwd=None, env=None):
        del env
        arguments = tuple(argv)
        if arguments == ("openspec", "--version"):
            return ProcessResult(arguments, 0, "1.7.0\n", "")
        assert cwd is not None
        (cwd / "partial").mkdir()
        return ProcessResult(arguments, 2, "", "generation failed")

    with pytest.raises(ManagedStateError, match="generation failed"):
        generate_openspec_skill_bundles(
            ("codex",),
            detected_version="1.7.0",
            temporary_parent=tmp_path,
            run=failing_generation,
        )
    assert list(tmp_path.iterdir()) == []
