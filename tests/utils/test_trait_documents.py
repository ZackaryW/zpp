import yaml

from zpp.utils.trait_documents import parse_trait_document, render_trait_document


def test_trait_document_round_trip_preserves_body_and_normalizes_metadata() -> None:
    source = """---
name: unicode
description: 保留方向
config:
  enabled: true
skill_lookup:
  - helper
---
\n""" + "  Keep this spacing.  \n"

    document = parse_trait_document(source, expected_name="unicode")

    assert document.name == "unicode"
    assert document.order is None
    assert document.config == {"enabled": True}
    assert document.skill_lookup == ("helper",)
    assert document.body == "\n  Keep this spacing.  \n"

    rendered = render_trait_document(document)
    metadata_text, body = rendered.removeprefix("---\n").split("---\n", 1)
    assert yaml.safe_load(metadata_text) == {
        "name": "unicode",
        "description": "保留方向",
        "order": None,
        "config": {"enabled": True},
        "skill_lookup": ["helper"],
    }
    assert body == document.body
