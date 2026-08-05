from __future__ import annotations

from pathlib import Path

import pytest

from zpp import __version__
from zpp.core.state import initialize_user_state
from zpp.core.updating import update_global_state
from zpp.utils.agent_bootstrap import inspect_agent_integrations
from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.models import ManagedStateError
from zpp.utils.openspec_projections import inspect_openspec_projection
from zpp.utils.openspec_skills import (
    GeneratedOpenSpecBundle,
    OPENSPEC_CORE_SKILL_NAMES,
)
from zpp.utils.skill_bundles import (
    SkillBundle,
    SkillFile,
    fingerprint_skill_files,
    load_packaged_skill_bundle,
)
from zpp.utils.skill_lifecycle import (
    mutation_plan_for_skill_lifecycle,
    plan_skill_install,
)
from zpp.utils.skill_projections import inspect_skill_scopes, skill_projection_roots


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(root).as_posix() or ".": (
            None if path.is_dir() else path.read_bytes()
        )
        for path in (root, *sorted(root.rglob("*")))
    }


def install_outdated_workflow(home: Path, agent: str) -> None:
    current = load_packaged_skill_bundle(__version__)
    historical = SkillBundle("0.8.0", current.files, current.fingerprint)
    projections = skill_projection_roots(
        home=home,
        target=None,
        scope="global",
        agents=(agent,),
    )
    inspected = inspect_skill_scopes(projections, historical)
    plan = plan_skill_install(historical, inspected, (), force=False)
    apply_mutation_plan(mutation_plan_for_skill_lifecycle(historical, plan))


def generated_bundles(agents, *, detected_version, **_kwargs):
    bundles = []
    for agent in agents:
        files = tuple(
            SkillFile(f"{name}/SKILL.md", f"{agent}:{name}\n".encode())
            for name in OPENSPEC_CORE_SKILL_NAMES
        )
        bundles.append(
            GeneratedOpenSpecBundle(
                agent,
                detected_version,
                files,
                fingerprint_skill_files(files),
            )
        )
    return tuple(bundles)


def test_global_update_discovers_and_completes_only_an_installed_workflow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialize_user_state(tmp_path)
    install_outdated_workflow(tmp_path, "pi")
    calls = []

    def generate(agents, *, detected_version, **kwargs):
        calls.append(tuple(agents))
        return generated_bundles(
            agents,
            detected_version=detected_version,
            **kwargs,
        )

    monkeypatch.setattr("zpp.core.updating.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr("zpp.core.updating.generate_openspec_skill_bundles", generate)

    assert update_global_state(tmp_path) == ("pi",)

    current = load_packaged_skill_bundle(__version__)
    inspection = inspect_skill_scopes(
        skill_projection_roots(
            home=tmp_path,
            target=None,
            scope="global",
            agents=("pi",),
        ),
        current,
    )[0]
    assert inspection.state == "compatible"
    assert inspect_agent_integrations(tmp_path, ("pi",))[0].status == "current"
    assert inspect_openspec_projection(
        tmp_path / ".pi/agent/skills",
        "pi",
        "1.7.0",
    ).state == "compatible"
    assert calls == [("pi",)]
    assert not (tmp_path / ".codex").exists()
    assert not (tmp_path / ".claude").exists()

    before = snapshot(tmp_path)
    calls.clear()
    assert update_global_state(tmp_path) == ("pi",)
    assert snapshot(tmp_path) == before
    assert calls == []


def test_global_update_preflights_every_surface_before_default_or_workflow_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialize_user_state(tmp_path)
    missing = tmp_path / ".zpp/profiles/default/traits/bdd-structure-python.md"
    missing.unlink()
    install_outdated_workflow(tmp_path, "pi")
    conflict = tmp_path / ".claude/skills/zpp-author-skill/SKILL.md"
    conflict.parent.mkdir(parents=True)
    conflict.write_text("unmanaged\n", encoding="utf-8")
    before = snapshot(tmp_path)
    monkeypatch.setattr("zpp.core.updating.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr(
        "zpp.core.updating.generate_openspec_skill_bundles",
        generated_bundles,
    )

    with pytest.raises(ManagedStateError, match=r"\.claude"):
        update_global_state(tmp_path)

    assert snapshot(tmp_path) == before
    assert not missing.exists()
