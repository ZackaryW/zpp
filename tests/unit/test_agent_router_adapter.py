from pathlib import Path
from types import SimpleNamespace

import pytest
from agent_router import ConflictError, Scope

from zpp.utils.agent_router import (
    ZPP_TRAITS_ARTIFACT_ID,
    ZppTraitArtifactExtension,
    project_workflow_skill,
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
