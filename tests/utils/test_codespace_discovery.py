from pathlib import Path

from zpp.utils.codespace_discovery import discover_codespace
from zpp.utils.codespace_models import CodespaceClaim, CodespaceMember
from zpp.utils.openspec_adapter import OpenSpecMember, OpenSpecWorkset


def _claim(root: Path) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        workset_name="zpp-instance",
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


def test_discovery_prefers_active_claim_then_reports_workset_ambiguity(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    other = tmp_path / "other"
    other.mkdir()
    first = OpenSpecWorkset("first", (OpenSpecMember("project", project),))
    second = OpenSpecWorkset("second", (OpenSpecMember("project", project),))

    active = discover_codespace(
        nested,
        claims=(_claim(project),),
        worksets=(first, second),
    )
    ambiguous = discover_codespace(
        nested,
        claims=(),
        worksets=(first, second),
    )
    absent = discover_codespace(other, claims=(), worksets=(first,))

    assert active.active_id == "instance"
    assert active.candidates == ()
    assert ambiguous.active_id is None
    assert [item.name for item in ambiguous.candidates] == ["first", "second"]
    assert absent.active_id is None and absent.candidates == ()
