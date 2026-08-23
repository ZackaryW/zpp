from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agent_router import AgentEnvironment, AgentRouter, Scope
from typer.testing import CliRunner

from zpp.artifacts import (
    packaged_companion_skills,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
from zpp.cli import app
from zpp.cli.reset import SUPPORTED_AGENTS

runner = CliRunner()


def _git_repository(repository: Path) -> None:
    repository.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)


def test_confirmed_reset_removes_every_agent_user_projection_through_router(
    tmp_path: Path,
    monkeypatch,
) -> None:
    user_home = tmp_path / "user"
    project = tmp_path / "project"
    user_home.mkdir()
    project.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: user_home))
    skill = packaged_workflow_skill()
    companion_skills = packaged_companion_skills()
    routers = {}
    for agent in SUPPORTED_AGENTS:
        router = AgentRouter(
            agent,
            home=user_home,
            environment=AgentEnvironment(user_home, project),
        )
        router.install_skill(skill, scope=Scope.USER)
        for companion_skill in companion_skills:
            router.install_skill(companion_skill, scope=Scope.USER)
        router.install_hook(packaged_workflow_hook(agent), scope=Scope.USER)
        routers[agent] = router

    zpp_home = tmp_path / "zpp-home"
    state = zpp_home / "bundler"
    state.mkdir(parents=True)
    (state / "old.json").write_text("old")
    result = runner.invoke(
        app,
        ["--path", str(zpp_home), "reset", "--yes"],
    )

    assert result.exit_code == 0, result.output
    assert not (state / "old.json").exists()
    for agent, router in routers.items():
        assert router.inspect_skill(skill, scope=Scope.USER).status == "absent"
        assert all(
            router.inspect_skill(companion_skill, scope=Scope.USER).status == "absent"
            for companion_skill in companion_skills
        )
        assert (
            router.inspect_hook(
                packaged_workflow_hook(agent),
                scope=Scope.USER,
            ).status
            == "absent"
        )


def test_init_regenerates_and_reset_force_removes_openspec_skills(
    tmp_path: Path,
    monkeypatch,
) -> None:
    user_home = tmp_path / "user"
    user_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: user_home))

    first = runner.invoke(app, ["init", "--agent", "codex"])
    second = runner.invoke(app, ["init", "--agent", "codex"])
    synced = runner.invoke(app, ["sync", "--agent", "codex"])
    detailed = runner.invoke(app, ["sync", "--agent", "codex", "--json"])

    assert first.exit_code == second.exit_code == 0
    assert synced.exit_code == detailed.exit_code == 0, synced.output
    companion_skills = packaged_companion_skills()
    expected = 2 + len(companion_skills) + 6
    assert first.stdout == f"Initialized 1 agent: {expected} installed.\n"
    assert "already initialized" in second.stdout
    assert "zpp sync" in second.stdout
    assert synced.stdout == (
        f"Synchronized: 0 reprojected, {expected} already current.\n"
    )
    assert len(json.loads(detailed.stdout)) == expected
    for name in (skill.name for skill in companion_skills):
        assert (user_home / ".codex/skills" / name / "SKILL.md").is_file()
    generated = user_home / ".codex/skills/openspec-apply-change"
    provenance = generated / ".zpp-openspec.json"
    assert provenance.is_file()
    assert json.loads(provenance.read_text())["generator"] == "zpp"

    (generated / "SKILL.md").write_text("modified", encoding="utf-8")
    zpp_home = tmp_path / "zpp-home"
    reset = runner.invoke(
        app,
        ["--path", str(zpp_home), "reset", "--yes"],
    )

    assert reset.exit_code == 0, reset.output
    assert not generated.exists()
    assert not (user_home / ".codex/skills/zpp-configure-behave").exists()
    assert not (user_home / ".codex/skills/zpp-author-trait").exists()
    assert (zpp_home / "bundler").is_dir()


def test_reset_preserves_modified_packaged_authoring_skill_and_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    user_home = tmp_path / "user"
    user_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: user_home))
    initialized = runner.invoke(app, ["init", "--agent", "codex"])
    assert initialized.exit_code == 0, initialized.output

    skill = user_home / ".codex/skills/zpp-author-trait/SKILL.md"
    skill.write_text(skill.read_text() + "\nlocal modification\n")
    zpp_home = tmp_path / "zpp-home"
    state = zpp_home / "bundler"
    state.mkdir(parents=True)
    marker = state / "old.json"
    marker.write_text("old")

    reset = runner.invoke(
        app,
        ["--path", str(zpp_home), "reset", "--yes"],
    )

    assert reset.exit_code == 2
    assert "zpp-author-trait" in reset.output
    assert skill.is_file()
    assert marker.read_text() == "old"


def test_no_space_repository_resolution_selects_python_and_flutter(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _git_repository(repository)
    local = repository / ".zpp"
    local.mkdir()
    (local / "zpp.toml").write_text(
        "[facet]\nlanguage=['python', 'flutter']\nbuild_tool='uv'\n"
    )
    before = sorted(path.relative_to(repository) for path in repository.rglob("*"))

    result = runner.invoke(
        app,
        [
            "--path",
            str(tmp_path / "state"),
            "resolve",
            str(repository),
            "--stage",
            "wire",
            "--explain",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    selected = [(item["family"], item["body"]) for item in payload["bodies"]]
    bdd = [body for family, body in selected if family == "bdd"]
    assert any("Behave" in body for body in bdd)
    assert any("Gherkin" in body for body in bdd)
    assert len(bdd) == 2
    context = json.loads(payload["ZPP_CONTEXT"])
    assert context["version"] == 2
    assert context["facets"]["language"] == ["python", "flutter"]
    assert "stage" not in context["facets"]
    assert [item["value"] for item in context["members"]["language"]] == [
        "python",
        "flutter",
    ]
    assert payload["explanation"]["families"]
    assert payload["explanation"]["context"]["values"]["stage"] == "wire"
    after = sorted(path.relative_to(repository) for path in repository.rglob("*"))
    assert after == before


def test_invalid_repository_trait_reports_clean_cli_error(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    _git_repository(repository)
    (traits / "bdd.toml").write_text("[meta]\nselection='first-win'\n[[trait]]\n")

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "resolve", str(repository)],
    )

    assert result.exit_code == 2
    assert "invalid trait document" in result.output
    assert "Traceback" not in result.output


def test_unknown_workflow_stage_reports_clean_cli_error(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _git_repository(repository)

    result = runner.invoke(
        app,
        ["resolve", str(repository), "--stage", "invented-stage"],
    )

    assert result.exit_code == 2
    assert "unsupported workflow stage" in result.output
    assert "Traceback" not in result.output


def test_manual_trait_requires_direct_query_and_uses_normal_matching(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    _git_repository(repository)
    (repository / ".zpp" / "zpp.toml").write_text("[facet]\nlanguage='python'\n")
    (traits / "manual-policy.toml").write_text(
        "[meta]\nselection='all'\nactivation='manual'\n"
        "[[trait]]\n[trait.facet]\nlanguage='python'\n"
        "[trait.content]\nbody='manual python policy'\n"
        "[[trait]]\n[trait.facet]\nlanguage='flutter'\n"
        "[trait.content]\nbody='manual flutter policy'\n"
    )

    common = runner.invoke(app, ["resolve", str(repository)])
    direct = runner.invoke(
        app,
        ["resolve", str(repository), "--trait", "manual-policy"],
    )

    assert common.exit_code == direct.exit_code == 0
    assert "manual python policy" not in common.stdout
    assert direct.stdout == "manual python policy"


def test_always_run_trait_bypasses_activation_and_preserves_extend(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    _git_repository(repository)
    (traits / "baseline.toml").write_text(
        "[meta]\nselection='extend'\nactivation='always-run'\n"
        "[[trait]]\n[trait.facet]\nlanguage='python'\n"
        "[trait.content]\nbody='generic python'\n"
        "[[trait]]\n[trait.facet]\nlanguage='python'\nbuild_tool='uv'\n"
        "[trait.content]\nbody='python uv'\n"
        "[[trait]]\n[trait.facet]\nlanguage='flutter'\n"
        "[trait.content]\nbody='flutter'\n"
    )

    result = runner.invoke(
        app,
        ["resolve", str(repository), "--trait", "baseline", "--explain"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [item["body"] for item in payload["bodies"]] == ["python uv", "flutter"]
    assert "language" not in json.loads(payload["ZPP_CONTEXT"])["facets"]


def test_unknown_direct_trait_query_returns_no_unrelated_output(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _git_repository(repository)

    result = runner.invoke(
        app,
        ["resolve", str(repository), "--trait", "unknown-family"],
    )

    assert result.exit_code == 2
    assert "unknown trait family" in result.output
    assert "Behave" not in result.output


def test_reconciled_packaged_families_resolve_by_their_current_boundaries(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _git_repository(repository)

    execution = runner.invoke(
        app,
        [
            "resolve",
            str(repository),
            "--trait",
            "bdd-execution",
            "--facet",
            "bdd_mode=complete",
        ],
    )
    common = runner.invoke(app, ["resolve", str(repository)])
    removed = runner.invoke(
        app,
        ["resolve", str(repository), "--trait", "lease-complete-affected-set"],
    )

    assert execution.exit_code == common.exit_code == 0
    assert "--all" in execution.stdout
    assert "Preserve current specifications" in common.stdout
    assert "logical leases" not in common.stdout
    assert removed.exit_code == 2
    assert "unknown trait family" in removed.output
