from __future__ import annotations

import tomllib
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from pathlib import Path, PurePath
from typing import Final, Protocol

from agent_router import (
    AgentRouter,
    ArtifactEffectiveState,
    ArtifactManifest,
    ArtifactStatus,
    Hook,
    LifecycleResult,
    PluginArtifactContext,
    Scope,
    Skill,
)

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind

ZPP_TRAITS_ARTIFACT_ID: Final[str] = "zpp.traits"
ZPP_TRAITS_CONTRACT_VERSION: Final[str] = "2"
FORMER_WORKFLOW_HOOK_NAME: Final[str] = "zpp-session"


@dataclass(frozen=True, slots=True)
class ZppTraitArtifactExtension:
    manifest: ArtifactManifest = field(
        default_factory=lambda: ArtifactManifest(
            ZPP_TRAITS_ARTIFACT_ID,
            ZPP_TRAITS_CONTRACT_VERSION,
        )
    )

    def locate(self, context: PluginArtifactContext) -> Iterable[PurePath]:
        root = context.root
        traits = root / "traits"
        if not traits.is_dir():
            return ()
        candidates = sorted(
            traits.glob("*.toml"),
            key=lambda path: (path.name.casefold(), path.name),
        )
        return tuple(PurePath(path.relative_to(root)) for path in candidates)


class _WorkflowRouter(Protocol):
    def inspect_skill(
        self,
        skill: Skill,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...

    def inspect_hook(
        self,
        hook: Hook,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...

    def install_skill(
        self,
        skill: Skill,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...

    def update_skill(
        self,
        skill: Skill,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...

    def uninstall_skill(
        self,
        name: str,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
        force: bool = False,
    ) -> LifecycleResult: ...

    def install_hook(
        self,
        hook: Hook,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...

    def uninstall_hook(
        self,
        name: str,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...


def active_trait_artifacts(
    router: AgentRouter,
) -> tuple[ArtifactStatus, ...]:
    return tuple(
        status
        for status in router.resolve_artifacts(ZPP_TRAITS_ARTIFACT_ID)
        if status.effective is ArtifactEffectiveState.ACTIVE
    )


def active_trait_sources(router: AgentRouter) -> tuple[BoundTraitSource, ...]:
    sources: list[BoundTraitSource] = []
    for source_order, status in enumerate(active_trait_artifacts(router), start=1):
        identifier = (
            f"agent-router:{status.ref.agent.value}:"
            f"{status.ref.scope}:{status.ref.native_ref}"
        )
        documents = tuple(
            BoundTraitDocument(
                family=path.stem,
                values=tomllib.loads(path.read_text(encoding="utf-8")),
                identifier=f"{identifier}:{path.name}",
                order=order,
                path=path,
            )
            for order, path in enumerate(status.paths)
            if path.suffix == ".toml"
        )
        if documents:
            sources.append(
                BoundTraitSource(
                    kind=SourceKind.GLOBAL,
                    identifier=identifier,
                    order=source_order,
                    documents=documents,
                )
            )
    return tuple(sources)


def project_workflow_skill(
    router: AgentRouter | _WorkflowRouter,
    skill: Skill,
    scope: Scope,
    project_root: Path | None,
    *,
    replace_project: bool = False,
) -> LifecycleResult:
    operation = router.update_skill if replace_project else router.install_skill
    return operation(
        skill,
        scope=scope,
        project_root=project_root,
    )


def inspect_workflow_skill(
    router: AgentRouter | _WorkflowRouter,
    skill: Skill,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    return router.inspect_skill(
        skill,
        scope=scope,
        project_root=project_root,
    )


def inspect_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    hook: Hook,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    return router.inspect_hook(
        hook,
        scope=scope,
        project_root=project_root,
    )


def former_workflow_hook(hook: Hook) -> Hook:
    """Derive the exact former ownership identity without another hook asset."""
    return replace(hook, name=FORMER_WORKFLOW_HOOK_NAME)


def _former_hook_migration_ready(current, former) -> bool:
    return current.status == "unmanaged" and former.status == "current"


def inspect_migratable_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    hook: Hook,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    """Expose an intact owned former hook as an outdated current projection."""
    current = inspect_workflow_hook(router, hook, scope, project_root)
    former = inspect_workflow_hook(
        router,
        former_workflow_hook(hook),
        scope,
        project_root,
    )
    if _former_hook_migration_ready(current, former):
        return replace(current, status="outdated")
    return current


def project_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    hook: Hook,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    return router.install_hook(hook, scope=scope, project_root=project_root)


def project_migratable_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    hook: Hook,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    """Replace only an intact Agent Router-owned former hook identity."""
    current = inspect_workflow_hook(router, hook, scope, project_root)
    former_hook = former_workflow_hook(hook)
    former = inspect_workflow_hook(router, former_hook, scope, project_root)
    if _former_hook_migration_ready(current, former):
        remove_workflow_hook(
            router,
            former_hook.name,
            scope,
            project_root,
        )
    return project_workflow_hook(router, hook, scope, project_root)


def reproject_workflow_skill(
    router: AgentRouter | _WorkflowRouter,
    skill: Skill,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    remove_workflow_skill(
        router,
        skill.name,
        scope,
        project_root,
        force=True,
    )
    return project_workflow_skill(router, skill, scope, project_root)


def reproject_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    hook: Hook,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    inspection = inspect_workflow_hook(router, hook, scope, project_root)
    if inspection.status == "current":
        remove_workflow_hook(router, hook.name, scope, project_root)
    return project_workflow_hook(router, hook, scope, project_root)


def remove_workflow_skill(
    router: AgentRouter | _WorkflowRouter,
    name: str,
    scope: Scope,
    project_root: Path | None,
    *,
    force: bool = False,
) -> LifecycleResult:
    if force:
        return router.uninstall_skill(
            name,
            scope=scope,
            project_root=project_root,
            force=True,
        )
    return router.uninstall_skill(
        name,
        scope=scope,
        project_root=project_root,
    )


def remove_workflow_hook(
    router: AgentRouter | _WorkflowRouter,
    name: str,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    return router.uninstall_hook(name, scope=scope, project_root=project_root)
