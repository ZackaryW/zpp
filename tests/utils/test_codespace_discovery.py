from pathlib import Path

from zpp.utils.codespace_discovery import discover_codespace
from zpp.utils.codespace_models import CodespaceClaim, CodespaceMember


def _claim(root: Path) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        members=(
            CodespaceMember(
                name="project",
                original_path=root,
                effective_path=root,
                checkout_key="claim-key",
                commit="abc",
                kind="project",
            ),
        ),
    )


def test_discovery_finds_an_active_claim_or_returns_none(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    other = tmp_path / "other"
    other.mkdir()
    active = discover_codespace(
        nested,
        claims=(_claim(project),),
    )
    absent = discover_codespace(other, claims=(_claim(project),))

    assert active == "instance"
    assert absent is None


def test_discovery_uses_only_active_claims_as_path_free_authority(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)

    assert discover_codespace(nested, claims=(_claim(project),)) == "instance"
    assert discover_codespace(tmp_path, claims=(_claim(project),)) is None
