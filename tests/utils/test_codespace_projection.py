from pathlib import Path

from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    CodespaceProjection,
)
from zpp.utils.codespace_projection import orphaned_codespace_projections
from zpp.utils.openspec_adapter import OpenSpecWorkset


def test_orphan_detection_only_returns_unrecorded_strict_zpp_projections(
    tmp_path: Path,
) -> None:
    claim = CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        members=(
            CodespaceMember(
                name="project",
                original_path=tmp_path,
                effective_path=tmp_path,
                checkout_key="key",
                commit="abc",
                kind="project",
            ),
        ),
        projection=CodespaceProjection(generation=2, structure_key="structure"),
    )
    worksets = tuple(
        OpenSpecWorkset(name, ())
        for name in (
            "zpp-instance-g1",
            "zpp-instance-g2",
            "zpp-orphan-g4",
            "zpp-instance-add-old",
            "user-workset",
        )
    )

    assert orphaned_codespace_projections(
        CodespaceIndex(claims={"instance": claim}),
        worksets,
    ) == ("zpp-instance-g1", "zpp-orphan-g4")
