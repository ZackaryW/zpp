from hashlib import sha256
from pathlib import Path

import pytest

from zpp.utils.models import ZppValidationError
from zpp.utils.trait_compiler import compile_trait_index


def test_compile_trait_index_returns_deterministic_normalized_records(
    tmp_path: Path,
) -> None:
    beta = tmp_path / "beta.md"
    beta.write_bytes(
        "---\nname: beta\ndescription: 第二\norder: 20\n---\n\nBeta body.\n".encode(
            "utf-8"
        )
    )
    alpha = tmp_path / "alpha.md"
    alpha.write_bytes(
        (
            "---\nname: alpha\ndescription: First\nconfig:\n  enabled: true\n"
            "skill_lookup:\n  - helper\n---\n\n  Alpha body.  \n"
        ).encode("utf-8")
    )

    index = compile_trait_index([beta, alpha])

    assert index == {
        "schema_version": 2,
        "traits": {
            "alpha": {
                "description": "First",
                "order": None,
                "config": {"enabled": True},
                "skill_lookup": ["helper"],
                "body": "\n  Alpha body.  \n",
                "source_sha256": sha256(alpha.read_bytes()).hexdigest(),
            },
            "beta": {
                "description": "第二",
                "order": 20,
                "config": {},
                "skill_lookup": [],
                "body": "\nBeta body.\n",
                "source_sha256": sha256(beta.read_bytes()).hexdigest(),
            },
        },
    }


def test_compile_trait_index_aggregates_every_source_error_and_duplicate(
    tmp_path: Path,
) -> None:
    missing_description = tmp_path / "missing.md"
    missing_description.write_text(
        "---\nname: missing\nunknown: true\n---\nBody\n",
        encoding="utf-8",
    )
    unsafe = tmp_path / "unsafe.md"
    unsafe.write_text(
        "---\n!!python/object:builtins.object {}\n---\nBody\n",
        encoding="utf-8",
    )
    first_duplicate = tmp_path / "one" / "same.md"
    first_duplicate.parent.mkdir()
    first_duplicate.write_text(
        "---\nname: same\ndescription: First\n---\nBody\n",
        encoding="utf-8",
    )
    second_duplicate = tmp_path / "two" / "same.md"
    second_duplicate.parent.mkdir()
    second_duplicate.write_text(
        "---\nname: same\ndescription: Second\n---\nBody\n",
        encoding="utf-8",
    )
    original_bytes = {
        path: path.read_bytes()
        for path in (missing_description, unsafe, first_duplicate, second_duplicate)
    }

    with pytest.raises(ZppValidationError) as caught:
        compile_trait_index(original_bytes)

    issue_sources = {issue.source for issue in caught.value.issues}
    assert {missing_description, unsafe, second_duplicate} <= issue_sources
    assert any("duplicate" in issue.message for issue in caught.value.issues)
    assert {path: path.read_bytes() for path in original_bytes} == original_bytes
