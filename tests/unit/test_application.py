from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import pytest

from zpp.core.application import (
    BoundTraitDocument,
    BoundTraitSource,
    TraitApplication,
    TraitInvocation,
)
from zpp.core.evidence import EvidenceRuntime
from zpp.core.models import SourceKind


def _document(body: str) -> BoundTraitDocument:
    return BoundTraitDocument(
        family="bdd",
        values=MappingProxyType(
            {
                "meta": {"selection": "first-win"},
                "trait": [
                    {
                        "facet": {"language": "python"},
                        "content": {"body": body},
                    }
                ],
            }
        ),
    )


def test_application_resolves_classified_sources_without_layout_assumptions(
    tmp_path: Path,
) -> None:
    sources = (
        BoundTraitSource(
            SourceKind.GLOBAL,
            "packaged-global",
            0,
            (_document("global body"),),
        ),
        BoundTraitSource(
            SourceKind.STORE,
            "selected-store",
            0,
            (_document("store body"),),
        ),
        BoundTraitSource(
            SourceKind.REPOSITORY,
            "selected-repository",
            0,
            (_document("repository body"),),
        ),
    )
    application = TraitApplication(
        lambda target: EvidenceRuntime(target, Path.read_bytes, lambda _tool: None)
    )

    result = application.resolve(
        TraitInvocation(
            target=tmp_path,
            stage="wire",
            facets=MappingProxyType({"language": "python"}),
            stored_context=None,
            repository_context=None,
            sources=sources,
        )
    )

    assert [item.body for item in result.bodies] == ["repository body"]
    assert result.explanation["families"][0]["policy_source"] == ("selected-repository")
    assert "artifacts/traits" not in str(result.explanation)
    assert result.resolution.context.values["stage"] == "wire"
    assert '"stage":"wire"' not in result.context
    assert result.explanation["context"]["members"]["language"] == [
        {"value": "python", "source": "invocation", "evidence": []}
    ]


def test_application_rejects_unknown_explicit_workflow_stage(
    tmp_path: Path,
) -> None:
    application = TraitApplication(
        lambda target: EvidenceRuntime(target, Path.read_bytes, lambda _tool: None)
    )

    with pytest.raises(ValueError, match="unsupported workflow stage"):
        application.resolve(
            TraitInvocation(
                target=tmp_path,
                stage="invented-stage",
                facets=MappingProxyType({}),
                stored_context=None,
                repository_context=None,
                sources=(),
            )
        )
