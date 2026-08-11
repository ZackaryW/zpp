import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from agent_router import (
    Agent,
    AgentEnvironment,
    AgentRouter,
    ArtifactEffectiveState,
    ConflictError,
    Scope,
    Skill,
)

from zpp.utils.agent_router import (
    ZPP_TRAITS_ARTIFACT_ID,
    ZppTraitArtifactExtension,
    active_trait_sources,
    project_workflow_hook,
    project_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
)


def test_trait_artifact_extension_locates_only_ordered_top_level_toml(
    tmp_path: Path,
) -> None:
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "z.toml").write_text("")
    (traits / "a.toml").write_text("")
    (traits / "ignored.md").write_text("")
    nested = traits / "nested"
    nested.mkdir()
    (nested / "ignored.toml").write_text("")
    extension = ZppTraitArtifactExtension()

    paths = tuple(extension.locate(SimpleNamespace(root=tmp_path)))

    assert extension.manifest.identifier == ZPP_TRAITS_ARTIFACT_ID
    assert [str(path) for path in paths] == ["traits/a.toml", "traits/z.toml"]


def test_project_workflow_skill_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def install_skill(self, skill, *, scope, project_root):
            self.call = (skill, scope, project_root)
            return expected

    router = Router()
    skill = object()
    project = Path("/repository")

    result = project_workflow_skill(router, skill, Scope.PROJECT, project)

    assert result is expected
    assert router.call == (skill, Scope.PROJECT, project)


def test_project_workflow_skill_preserves_router_conflict() -> None:
    class Router:
        def install_skill(self, skill, *, scope, project_root):
            raise ConflictError("conflicting skill destination")

    with pytest.raises(ConflictError, match="conflicting skill destination"):
        project_workflow_skill(Router(), object(), Scope.USER, None)


def test_project_workflow_skill_uses_explicit_project_update() -> None:
    expected = object()

    class Router:
        def update_skill(self, skill, *, scope, project_root):
            self.call = (skill, scope, project_root)
            return expected

    router = Router()
    skill = object()
    project = Path("/repository")

    result = project_workflow_skill(
        router,
        skill,
        Scope.PROJECT,
        project,
        replace_project=True,
    )

    assert result is expected
    assert router.call == (skill, Scope.PROJECT, project)


def test_project_workflow_hook_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def install_hook(self, hook, *, scope, project_root):
            self.call = (hook, scope, project_root)
            return expected

    router = Router()
    hook = object()
    project = Path("/repository")

    result = project_workflow_hook(router, hook, Scope.PROJECT, project)

    assert result is expected
    assert router.call == (hook, Scope.PROJECT, project)


def test_remove_workflow_skill_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def uninstall_skill(self, name, *, scope, project_root):
            self.call = (name, scope, project_root)
            return expected

    router = Router()
    project = Path("/repository")

    result = remove_workflow_skill(router, "zpp-workflow", Scope.PROJECT, project)

    assert result is expected
    assert router.call == ("zpp-workflow", Scope.PROJECT, project)


def test_remove_workflow_hook_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def uninstall_hook(self, name, *, scope, project_root):
            self.call = (name, scope, project_root)
            return expected

    router = Router()
    project = Path("/repository")

    result = remove_workflow_hook(router, "zpp-session", Scope.PROJECT, project)

    assert result is expected
    assert router.call == ("zpp-session", Scope.PROJECT, project)


def test_active_trait_sources_use_only_router_selected_toml(tmp_path: Path) -> None:
    trait = tmp_path / "bdd.toml"
    trait.write_text(
        "[meta]\nselection='first-win'\n[[trait]]\n[trait.content]\nbody='plugin'\n"
    )
    ignored = tmp_path / "ignored.md"
    ignored.write_text("ignored")

    class Router:
        def resolve_artifacts(self, identifier):
            assert identifier == ZPP_TRAITS_ARTIFACT_ID
            ref = SimpleNamespace(
                agent=Agent.CODEX,
                scope="project",
                native_ref="owner/plugin",
            )
            return (
                SimpleNamespace(
                    effective=ArtifactEffectiveState.INACTIVE,
                    ref=ref,
                    paths=(trait,),
                ),
                SimpleNamespace(
                    effective=ArtifactEffectiveState.ACTIVE,
                    ref=ref,
                    paths=(trait, ignored),
                ),
            )

    sources = active_trait_sources(Router())

    assert len(sources) == 1
    assert sources[0].identifier.endswith("project:owner/plugin")
    assert [item.family for item in sources[0].documents] == ["bdd"]
    assert sources[0].documents[0].values["trait"][0]["content"]["body"] == "plugin"


def test_real_agent_router_owns_project_install_update_and_remove(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    subprocess.run(
        ["git", "init"],
        cwd=project,
        check=True,
        capture_output=True,
    )
    router = AgentRouter(
        Agent.CODEX,
        home=home,
        environment=AgentEnvironment(home, project),
    )

    def skill(body: str) -> Skill:
        source = tmp_path / f"source-{body}"
        source.mkdir()
        (source / "SKILL.md").write_text(
            "---\n"
            "name: zpp-workflow\n"
            "description: Run the complete ZPP workflow.\n"
            "---\n"
            f"{body}\n"
        )
        return Skill.from_path(source)

    installed = project_workflow_skill(router, skill("first"), Scope.PROJECT, project)
    updated = project_workflow_skill(
        router,
        skill("second"),
        Scope.PROJECT,
        project,
        replace_project=True,
    )
    removed = remove_workflow_skill(router, "zpp-workflow", Scope.PROJECT, project)

    assert installed.status == "installed"
    assert updated.status == "updated"
    assert removed.status == "removed"
    assert not (removed.destination / "zpp-workflow").exists()

    unmanaged = removed.destination / "zpp-workflow"
    unmanaged.mkdir(parents=True)
    (unmanaged / "SKILL.md").write_text("unmanaged")
    with pytest.raises(ConflictError, match="conflicting skill destination"):
        project_workflow_skill(router, skill("third"), Scope.PROJECT, project)
