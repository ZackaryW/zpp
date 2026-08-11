from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Final, Protocol

from agent_router import (
    AgentRouter,
    ArtifactManifest,
    LifecycleResult,
    PluginArtifactContext,
    Scope,
    Skill,
)

ZPP_TRAITS_ARTIFACT_ID: Final[str] = "zpp.traits"
ZPP_TRAITS_CONTRACT_VERSION: Final[str] = "2"


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
    def install_skill(
        self,
        skill: Skill,
        *,
        scope: Scope,
        project_root: str | Path | None = None,
    ) -> LifecycleResult: ...


def project_workflow_skill(
    router: AgentRouter | _WorkflowRouter,
    skill: Skill,
    scope: Scope,
    project_root: Path | None,
) -> LifecycleResult:
    return router.install_skill(
        skill,
        scope=scope,
        project_root=project_root,
    )
