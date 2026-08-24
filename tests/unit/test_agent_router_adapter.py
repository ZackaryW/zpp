import json
import subprocess
from dataclasses import dataclass
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

from zpp.artifacts import packaged_workflow_hook
from zpp.utils.agent_router import (
    FORMER_WORKFLOW_HOOK_NAME,
    ZPP_TRAITS_ARTIFACT_ID,
    ZppTraitArtifactExtension,
    active_trait_sources,
    former_workflow_hook,
    inspect_migratable_workflow_hook,
    inspect_workflow_hook,
    inspect_workflow_skill,
    project_migratable_workflow_hook,
    project_workflow_hook,
    project_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
    reproject_workflow_hook,
    reproject_workflow_skill,
)


@dataclass(frozen=True)
class HookResult:
    status: str


@dataclass(frozen=True)
class HookStub:
    name: str


def test_former_workflow_hook_changes_only_the_ownership_name() -> None:
    current = packaged_workflow_hook(Agent.CODEX)

    former = former_workflow_hook(current)

    assert former.name == FORMER_WORKFLOW_HOOK_NAME
    assert former.fragment is current.fragment


@pytest.mark.parametrize("former_status", ["absent", "unmanaged", "conflict"])
def test_inspect_migratable_workflow_hook_preserves_unowned_current_state(
    former_status: str,
) -> None:
    current = HookStub("zpp-traits")
    observations = {
        "zpp-traits": HookResult("unmanaged"),
        FORMER_WORKFLOW_HOOK_NAME: HookResult(former_status),
    }

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            assert scope is Scope.USER
            assert project_root is None
            return observations[hook.name]

    result = inspect_migratable_workflow_hook(Router(), current, Scope.USER, None)

    assert result is observations["zpp-traits"]
    assert result.status == "unmanaged"


def test_inspect_migratable_workflow_hook_promotes_intact_former_ownership() -> None:
    current = HookStub("zpp-traits")

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            status = "unmanaged" if hook.name == "zpp-traits" else "current"
            return HookResult(status)

    result = inspect_migratable_workflow_hook(
        Router(), current, Scope.PROJECT, Path("/repository")
    )

    assert result.status == "outdated"


def test_project_migratable_workflow_hook_revalidates_removes_and_installs() -> None:
    current = HookStub("zpp-traits")
    project = Path("/repository")
    events = []
    expected = object()

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            events.append(("inspect", hook.name, scope, project_root))
            status = "unmanaged" if hook.name == "zpp-traits" else "current"
            return SimpleNamespace(status=status)

        def uninstall_hook(self, name, *, scope, project_root):
            events.append(("remove", name, scope, project_root))
            return SimpleNamespace(status="removed")

        def install_hook(self, hook, *, scope, project_root):
            events.append(("install", hook.name, scope, project_root))
            return expected

    result = project_migratable_workflow_hook(Router(), current, Scope.PROJECT, project)

    assert result is expected
    assert events == [
        ("inspect", "zpp-traits", Scope.PROJECT, project),
        ("inspect", FORMER_WORKFLOW_HOOK_NAME, Scope.PROJECT, project),
        ("remove", FORMER_WORKFLOW_HOOK_NAME, Scope.PROJECT, project),
        ("install", "zpp-traits", Scope.PROJECT, project),
    ]


def test_project_migratable_hook_installs_when_both_identities_absent() -> None:
    current = HookStub("zpp-traits")
    expected = object()

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            return HookResult("absent")

        def install_hook(self, hook, *, scope, project_root):
            assert hook is current
            assert scope is Scope.USER
            assert project_root is None
            return expected

    result = project_migratable_workflow_hook(Router(), current, Scope.USER, None)

    assert result is expected


def test_real_agent_router_migrates_former_project_hook_ownership(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    router = AgentRouter(
        Agent.CODEX,
        home=home,
        environment=AgentEnvironment(home, project),
    )
    current = packaged_workflow_hook(Agent.CODEX)
    installed = router.install_hook(
        former_workflow_hook(current),
        scope=Scope.PROJECT,
        project_root=project,
    )

    observed = inspect_migratable_workflow_hook(router, current, Scope.PROJECT, project)
    migrated = project_migratable_workflow_hook(router, current, Scope.PROJECT, project)

    assert installed.status == "installed"
    assert observed.status == "outdated"
    assert migrated.status == "installed"
    assert (
        router.inspect_hook(current, scope=Scope.PROJECT, project_root=project).status
        == "current"
    )
    assert (
        router.inspect_hook(
            former_workflow_hook(current),
            scope=Scope.PROJECT,
            project_root=project,
        ).status
        == "unmanaged"
    )


def test_real_agent_router_preserves_modified_former_project_hook(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    router = AgentRouter(
        Agent.CODEX,
        home=home,
        environment=AgentEnvironment(home, project),
    )
    current = packaged_workflow_hook(Agent.CODEX)
    former = former_workflow_hook(current)
    router.install_hook(former, scope=Scope.PROJECT, project_root=project)
    document_path = project / ".codex" / "hooks.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))
    handler = document["hooks"]["SessionStart"][0]["hooks"][0]
    handler["command"] += " --modified"
    modified = json.dumps(document, indent=2, sort_keys=True) + "\n"
    document_path.write_text(modified, encoding="utf-8")

    observed = inspect_migratable_workflow_hook(router, current, Scope.PROJECT, project)

    assert observed.status == "absent"
    assert (
        router.inspect_hook(former, scope=Scope.PROJECT, project_root=project).status
        == "outdated"
    )
    with pytest.raises(ConflictError):
        project_migratable_workflow_hook(router, current, Scope.PROJECT, project)
    assert document_path.read_text(encoding="utf-8") == modified


def test_reproject_workflow_skill_force_removes_then_installs() -> None:
    events = []
    expected = object()

    class Router:
        def uninstall_skill(self, name, *, scope, project_root, force=False):
            events.append(("remove", name, scope, project_root, force))
            return SimpleNamespace(status="removed")

        def install_skill(self, skill, *, scope, project_root):
            events.append(("install", skill, scope, project_root))
            return expected

    router = Router()
    skill = SimpleNamespace(name="zpp-workflow")

    result = reproject_workflow_skill(router, skill, Scope.USER, None)

    assert result is expected
    assert events == [
        ("remove", "zpp-workflow", Scope.USER, None, True),
        ("install", skill, Scope.USER, None),
    ]


def test_reproject_workflow_hook_removes_current_then_installs() -> None:
    events = []
    expected = object()

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            events.append(("inspect", hook, scope, project_root))
            return SimpleNamespace(status="current")

        def uninstall_hook(self, name, *, scope, project_root):
            events.append(("remove", name, scope, project_root))

        def install_hook(self, hook, *, scope, project_root):
            events.append(("install", hook, scope, project_root))
            return expected

    router = Router()
    hook = SimpleNamespace(name="zpp-traits")

    result = reproject_workflow_hook(router, hook, Scope.USER, None)

    assert result is expected
    assert events == [
        ("inspect", hook, Scope.USER, None),
        ("remove", "zpp-traits", Scope.USER, None),
        ("install", hook, Scope.USER, None),
    ]


def test_inspect_workflow_skill_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def inspect_skill(self, skill, *, scope, project_root):
            self.call = (skill, scope, project_root)
            return expected

    router = Router()
    skill = object()

    result = inspect_workflow_skill(router, skill, Scope.USER, None)

    assert result is expected
    assert router.call == (skill, Scope.USER, None)


def test_inspect_workflow_hook_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def inspect_hook(self, hook, *, scope, project_root):
            self.call = (hook, scope, project_root)
            return expected

    router = Router()
    hook = object()

    result = inspect_workflow_hook(router, hook, Scope.USER, None)

    assert result is expected
    assert router.call == (hook, Scope.USER, None)


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
    assert [path.as_posix() for path in paths] == ["traits/a.toml", "traits/z.toml"]


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


def test_remove_workflow_skill_forwards_explicit_force() -> None:
    expected = object()

    class Router:
        def uninstall_skill(self, name, *, scope, project_root, force=False):
            self.call = (name, scope, project_root, force)
            return expected

    router = Router()

    result = remove_workflow_skill(
        router,
        "openspec-apply-change",
        Scope.USER,
        None,
        force=True,
    )

    assert result is expected
    assert router.call == ("openspec-apply-change", Scope.USER, None, True)


def test_remove_workflow_hook_delegates_exact_arguments() -> None:
    expected = object()

    class Router:
        def uninstall_hook(self, name, *, scope, project_root):
            self.call = (name, scope, project_root)
            return expected

    router = Router()
    project = Path("/repository")

    result = remove_workflow_hook(router, "zpp-traits", Scope.PROJECT, project)

    assert result is expected
    assert router.call == ("zpp-traits", Scope.PROJECT, project)


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
