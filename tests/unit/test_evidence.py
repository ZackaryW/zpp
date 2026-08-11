from pathlib import Path

from zpp.catalog import decode_trait_document
from zpp.composition import compose_trait_family
from zpp.evidence import (
    EvidenceRequest,
    EvidenceRuntime,
    collect_evidence,
    evidence_requests,
)
from zpp.models import EvidenceBranch, EvidenceRef, FileContains, SourceKind, SourceRef


def test_collect_evidence_combines_bounded_predicates_and_records_uv_fact(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\ndependencies=['click']\n")
    request = EvidenceRequest(
        ref=EvidenceRef("bdd", 0, 0),
        branch=EvidenceBranch(
            workspace_contains="/pyproject.toml",
            file_contains=FileContains("/pyproject.toml", "click"),
            which="uv",
        ),
    )

    results = collect_evidence(
        [request],
        EvidenceRuntime(
            target=project,
            read_bytes=Path.read_bytes,
            executable=lambda tool: "/opt/bin/uv" if tool == "uv" else None,
        ),
    )

    result = results[request.ref]
    assert result.matched is True
    assert result.facts == {"has_uv": True}
    assert set(result.fingerprints) == {
        "workspace_contains:/pyproject.toml",
        "file_contains:/pyproject.toml:click",
        "which:uv",
    }


def test_root_anchored_workspace_pattern_rejects_nested_substitute(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    (nested / "pyproject.toml").write_text("nested")
    anchored = EvidenceRequest(
        EvidenceRef("bdd", 0, 0),
        EvidenceBranch(workspace_contains="/pyproject.toml"),
    )
    recursive = EvidenceRequest(
        EvidenceRef("bdd", 1, 0),
        EvidenceBranch(workspace_contains="pyproject.toml"),
    )

    results = collect_evidence(
        [anchored, recursive],
        EvidenceRuntime(project, Path.read_bytes, lambda _: None),
    )

    assert results[anchored.ref].matched is False
    assert results[recursive.ref].matched is True


def test_file_contains_is_literal_and_confined_to_target(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "data.txt").write_text("a.*b")
    (tmp_path / "secret.txt").write_text("secret")
    literal = EvidenceRequest(
        EvidenceRef("bdd", 0, 0),
        EvidenceBranch(file_contains=FileContains("/data.txt", "a.*b")),
    )
    escape = EvidenceRequest(
        EvidenceRef("bdd", 1, 0),
        EvidenceBranch(file_contains=FileContains("../secret.txt", "secret")),
    )

    results = collect_evidence(
        [literal, escape],
        EvidenceRuntime(project, Path.read_bytes, lambda _: None),
    )

    assert results[literal.ref].matched is True
    assert results[escape.ref].matched is False


def test_unavailable_executable_records_false_boolean_fact(tmp_path: Path) -> None:
    request = EvidenceRequest(
        EvidenceRef("tooling", 0, 0),
        EvidenceBranch(which="uv"),
    )

    result = collect_evidence(
        [request],
        EvidenceRuntime(tmp_path, Path.read_bytes, lambda _: None),
    )[request.ref]

    assert result.matched is False
    assert result.facts == {"has_uv": False}


def test_evidence_requests_preserve_family_flavor_and_branch_order() -> None:
    bdd = compose_trait_family(
        "bdd",
        [
            decode_trait_document(
                "bdd",
                {
                    "meta": {"selection": "all"},
                    "trait": [
                        {
                            "when": [
                                {"workspace_contains": "/pyproject.toml"},
                                {"which": "uv"},
                            ],
                            "content": {"body": "bdd"},
                        }
                    ],
                },
                SourceRef(SourceKind.GLOBAL, "global"),
            )
        ],
    )
    build = compose_trait_family(
        "build",
        [
            decode_trait_document(
                "build",
                {
                    "meta": {"selection": "first-win"},
                    "trait": [{"content": {"body": "build"}}],
                },
                SourceRef(SourceKind.GLOBAL, "global"),
            )
        ],
    )

    requests = evidence_requests([bdd, build])

    assert [request.ref for request in requests] == [
        EvidenceRef("bdd", 0, 0),
        EvidenceRef("bdd", 0, 1),
    ]
