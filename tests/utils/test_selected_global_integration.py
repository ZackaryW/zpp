import json
from pathlib import Path

import pytest

from zpp import __version__
from zpp.core.errors import ZppDomainError
from zpp.core.state import initialize_user_state
from zpp.core.skills import plan_selected_global_integration
from zpp.utils.agent_bootstrap import inspect_agent_integrations
from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.openspec_projections import inspect_openspec_projection
from zpp.utils.openspec_projections import plan_openspec_projection
from zpp.utils.openspec_skills import GeneratedOpenSpecBundle, OPENSPEC_CORE_SKILL_NAMES
from zpp.utils.models import ManagedStateError
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


def _snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(root).as_posix() or ".": (
            None if path.is_dir() else path.read_bytes()
        )
        for path in (root, *sorted(root.rglob("*")))
    }


def _generated_bundles(agents, *, detected_version, **_kwargs):
    result = []
    for agent in agents:
        files = tuple(
            SkillFile(f"{name}/SKILL.md", f"{agent}:{name}\n".encode())
            for name in OPENSPEC_CORE_SKILL_NAMES
        )
        result.append(
            GeneratedOpenSpecBundle(
                agent,
                detected_version,
                files,
                fingerprint_skill_files(files),
            )
        )
    return tuple(result)


def test_selected_global_integration_rejects_an_empty_selection(
    tmp_path: Path,
) -> None:
    with pytest.raises(ZppDomainError, match="at least one agent"):
        plan_selected_global_integration(
            home=tmp_path,
            agents=(),
            upgrade_default_profile=False,
        )


def test_selected_global_integration_plans_absent_deduplicated_agents_without_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialize_user_state(tmp_path)
    before = _snapshot(tmp_path)
    generated: list[tuple[str, ...]] = []

    def generate(agents, *, detected_version, **kwargs):
        generated.append(tuple(agents))
        return _generated_bundles(
            agents,
            detected_version=detected_version,
            **kwargs,
        )

    monkeypatch.setattr("zpp.core.skills.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr("zpp.core.skills.generate_openspec_skill_bundles", generate)

    plan = plan_selected_global_integration(
        home=tmp_path,
        agents=("codex", "codex", "pi"),
        upgrade_default_profile=False,
    )

    assert plan.actions == ("install", "install")
    assert generated == [("codex", "pi")]
    assert _snapshot(tmp_path) == before

    apply_mutation_plan(plan.mutation)
    bundle = load_packaged_skill_bundle(__version__)
    assert tuple(
        item.state
        for item in inspect_skill_scopes(
            skill_projection_roots(
                home=tmp_path,
                target=None,
                scope="global",
                agents=("codex", "pi"),
            ),
            bundle,
        )
    ) == ("compatible", "compatible")
    assert tuple(
        item.status
        for item in inspect_agent_integrations(tmp_path, ("codex", "pi"))
    ) == ("current", "current")
    assert inspect_openspec_projection(
        tmp_path / ".codex/skills",
        "codex",
        "1.7.0",
    ).state == "compatible"
    assert inspect_openspec_projection(
        tmp_path / ".pi/agent/skills",
        "pi",
        "1.7.0",
    ).state == "compatible"


def test_selected_global_integration_replaces_intact_outdated_owned_projections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialize_user_state(tmp_path)
    current = load_packaged_skill_bundle(__version__)
    historical = SkillBundle("0.8.0", current.files, current.fingerprint)
    workflow_projections = skill_projection_roots(
        home=tmp_path,
        target=None,
        scope="global",
        agents=("codex",),
    )
    historical_state = inspect_skill_scopes(workflow_projections, historical)
    apply_mutation_plan(
        mutation_plan_for_skill_lifecycle(
            historical,
            plan_skill_install(historical, historical_state, (), force=False),
        )
    )
    openspec_root = tmp_path / ".codex/skills"
    old_openspec = _generated_bundles(
        ("codex",),
        detected_version="1.6.0",
    )[0]
    apply_mutation_plan(
        plan_openspec_projection(
            openspec_root,
            old_openspec,
            inspect_openspec_projection(openspec_root, "codex", "1.6.0"),
        )
    )
    unrelated = openspec_root / "user-skill/SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep\n", encoding="utf-8")
    before = _snapshot(tmp_path)
    monkeypatch.setattr("zpp.core.skills.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr(
        "zpp.core.skills.generate_openspec_skill_bundles",
        _generated_bundles,
    )

    plan = plan_selected_global_integration(
        home=tmp_path,
        agents=("codex",),
        upgrade_default_profile=False,
    )

    assert plan.actions == ("replace",)
    assert _snapshot(tmp_path) == before
    apply_mutation_plan(plan.mutation)
    assert inspect_skill_scopes(workflow_projections, current)[0].state == "compatible"
    assert inspect_openspec_projection(
        openspec_root,
        "codex",
        "1.7.0",
    ).state == "compatible"
    assert unrelated.read_text(encoding="utf-8") == "keep\n"


@pytest.mark.parametrize("conflict_kind", ("workflow", "openspec", "hook"))
def test_selected_global_integration_rejects_every_selected_conflict_without_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    conflict_kind: str,
) -> None:
    initialize_user_state(tmp_path)
    if conflict_kind == "workflow":
        destination = tmp_path / ".codex/skills/zpp-clarify-change/SKILL.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("unmanaged\n", encoding="utf-8")
    elif conflict_kind == "openspec":
        destination = tmp_path / ".codex/skills/openspec-apply-change/SKILL.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("unmanaged\n", encoding="utf-8")
    else:
        destination = tmp_path / ".codex/hooks.json"
        destination.parent.mkdir(parents=True)
        destination.write_text(
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "matcher": "startup",
                                "hooks": [
                                    {"type": "command", "command": "zpp resolve"}
                                ],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
    before = _snapshot(tmp_path)
    monkeypatch.setattr("zpp.core.skills.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr(
        "zpp.core.skills.generate_openspec_skill_bundles",
        _generated_bundles,
    )

    with pytest.raises(ManagedStateError):
        plan_selected_global_integration(
            home=tmp_path,
            agents=("codex",),
            upgrade_default_profile=False,
        )

    assert _snapshot(tmp_path) == before


def test_selected_global_integration_applies_only_the_requested_profile_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialize_user_state(tmp_path)
    monkeypatch.setattr("zpp.core.skills.detect_openspec_version", lambda: "1.7.0")
    monkeypatch.setattr(
        "zpp.core.skills.generate_openspec_skill_bundles",
        _generated_bundles,
    )
    initial = plan_selected_global_integration(
        home=tmp_path,
        agents=("codex",),
        upgrade_default_profile=False,
    )
    apply_mutation_plan(initial.mutation)
    missing = tmp_path / ".zpp/profiles/default/traits/bdd-structure-python.md"
    missing.unlink()
    before_without_upgrade = _snapshot(tmp_path)

    without_upgrade = plan_selected_global_integration(
        home=tmp_path,
        agents=("codex",),
        upgrade_default_profile=False,
    )
    assert _snapshot(tmp_path) == before_without_upgrade
    apply_mutation_plan(without_upgrade.mutation)
    assert not missing.exists()
    assert _snapshot(tmp_path) == before_without_upgrade

    agent_before_upgrade = _snapshot(tmp_path / ".codex")
    with_upgrade = plan_selected_global_integration(
        home=tmp_path,
        agents=("codex",),
        upgrade_default_profile=True,
    )
    assert not missing.exists()
    apply_mutation_plan(with_upgrade.mutation)
    assert missing.is_file()
    assert _snapshot(tmp_path / ".codex") == agent_before_upgrade
