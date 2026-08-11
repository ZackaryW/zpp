import json
from types import MappingProxyType

import pytest

from zpp.models import (
    FacetContext,
    ResolutionContext,
    ResolutionResult,
    TargetIdentity,
)
from zpp.session import (
    SessionContextError,
    build_resolution_context,
    complete_stored_context,
    encode_session_context,
    restore_session_context,
)


def test_restore_session_context_invalidates_only_drifted_evidence_values() -> None:
    raw = json.dumps(
        {
            "version": 1,
            "target": {"repository": "/repo"},
            "facets": {"language": "python", "build_tool": "uv"},
            "provenance": {
                "language": {
                    "source": "evidence",
                    "evidence": ["workspace:/pyproject.toml"],
                },
                "build_tool": {"source": "repository", "evidence": []},
            },
            "fingerprints": {"workspace:/pyproject.toml": "old"},
        }
    )

    restored = restore_session_context(
        raw,
        TargetIdentity(repository="/repo"),
        {"workspace:/pyproject.toml": "new"},
    )

    assert restored.values == {"build_tool": "uv"}
    assert set(restored.provenance) == {"build_tool"}


def test_restore_session_context_ignores_another_target() -> None:
    raw = json.dumps(
        {
            "version": 1,
            "target": {"repository": "/other"},
            "facets": {"language": "python"},
            "provenance": {
                "language": {"source": "evidence", "evidence": []}
            },
            "fingerprints": {},
        }
    )

    restored = restore_session_context(
        raw, TargetIdentity(repository="/repo"), {}
    )

    assert restored.values == {}
    assert restored.target.repository == "/repo"


def test_restore_session_context_rejects_malformed_or_incomplete_json() -> None:
    with pytest.raises(SessionContextError, match="invalid ZPP_CONTEXT"):
        restore_session_context(
            '{"version":1,"target":',
            TargetIdentity(repository="/repo"),
            {},
        )

    with pytest.raises(SessionContextError, match="invalid ZPP_CONTEXT"):
        restore_session_context(
            json.dumps(
                {
                    "version": 1,
                    "target": {"repository": "/repo"},
                    "facets": {"language": "python"},
                    "provenance": {},
                    "fingerprints": {},
                }
            ),
            TargetIdentity(repository="/repo"),
            {},
        )


def test_encode_session_context_is_deterministic_and_round_trips_lists() -> None:
    raw = json.dumps(
        {
            "version": 1,
            "target": {"repository": "/repo"},
            "facets": {"language": ["python", "flutter"], "has_uv": True},
            "provenance": {
                "language": {"source": "evidence", "evidence": []},
                "has_uv": {"source": "evidence", "evidence": []},
            },
            "fingerprints": {},
        }
    )
    restored = restore_session_context(raw, TargetIdentity("/repo"), {})

    encoded = encode_session_context(restored)

    assert encoded == encode_session_context(restored)
    assert restore_session_context(encoded, TargetIdentity("/repo"), {}) == restored


def test_build_resolution_context_applies_context_precedence() -> None:
    stored = restore_session_context(
        json.dumps(
            {
                "version": 1,
                "target": {"repository": "/repo"},
                "facets": {"language": "stored", "build_tool": "stored"},
                "provenance": {
                    "language": {"source": "stored", "evidence": []},
                    "build_tool": {"source": "stored", "evidence": []},
                },
                "fingerprints": {},
            }
        ),
        TargetIdentity("/repo"),
        {},
    )
    repository = FacetContext(
        MappingProxyType({"language": "repository", "framework": "click"}),
        MappingProxyType({"language": "repository", "framework": "repository"}),
    )
    invocation = FacetContext(
        MappingProxyType({"language": "invocation", "stage": "shape"}),
        MappingProxyType({"language": "invocation", "stage": "invocation"}),
    )

    context = build_resolution_context(invocation, repository, stored)

    assert context.values == {
        "language": "invocation",
        "build_tool": "stored",
        "framework": "click",
        "stage": "shape",
    }


def test_complete_stored_context_preserves_resolution_provenance() -> None:
    resolution = ResolutionResult(
        families=(),
        context=ResolutionContext(
            values=MappingProxyType(
                {"framework": "click", "language": "python", "has_uv": False}
            ),
            provenance=MappingProxyType(
                {
                    "framework": "repository",
                    "language": "evidence",
                    "has_uv": "evidence",
                }
            ),
            evidence=MappingProxyType(
                {
                    "language": ("workspace:/pyproject.toml",),
                    "has_uv": ("which:uv",),
                }
            ),
            fingerprints=MappingProxyType(
                {
                    "workspace:/pyproject.toml": "present",
                    "which:uv": "missing",
                    "unused": "ignored",
                }
            ),
        ),
    )

    stored = complete_stored_context(resolution, TargetIdentity("/repo"))

    assert stored.target.repository == "/repo"
    assert stored.values == resolution.context.values
    assert stored.provenance["framework"].evidence == ()
    assert stored.provenance["language"].evidence == (
        "workspace:/pyproject.toml",
    )
    assert stored.fingerprints == {
        "workspace:/pyproject.toml": "present",
        "which:uv": "missing",
    }
    encoded = encode_session_context(stored)
    assert restore_session_context(
        encoded,
        TargetIdentity("/repo"),
        stored.fingerprints,
    ) == stored
