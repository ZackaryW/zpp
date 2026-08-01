from __future__ import annotations

import re
from typing import Sequence

from zpp.utils.codespace_identity import projection_name
from zpp.utils.codespace_models import CodespaceIndex
from zpp.utils.openspec_adapter import OpenSpecWorkset


_PROJECTION_NAME = re.compile(r"^zpp-.+-g[1-9][0-9]*$")


def orphaned_codespace_projections(
    index: CodespaceIndex,
    worksets: Sequence[OpenSpecWorkset],
) -> tuple[str, ...]:
    active = {
        projection_name(claim.instance_id, claim.projection.generation)
        for claim in index.claims.values()
        if claim.projection is not None
    }
    return tuple(
        workset.name
        for workset in worksets
        if _PROJECTION_NAME.fullmatch(workset.name) and workset.name not in active
    )
