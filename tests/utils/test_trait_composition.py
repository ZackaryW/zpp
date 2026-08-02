from zpp.utils.models import LayerConfig
from zpp.utils.trait_composition import (
    apply_trait_config_overlays,
    order_effective_traits,
    select_effective_documents,
)


def test_effective_traits_replace_overlay_shallowly_and_order_stably() -> None:
    indexes = (
        {
            "schema_version": 1,
            "traits": {
                "alpha": {
                    "description": "Old",
                    "order": 1,
                    "config": {"old": True},
                    "skill_lookup": [],
                    "body": "Old",
                },
                "beta": {
                    "description": "Beta",
                    "order": 10,
                    "config": {"nested": {"first": 1}, "keep": True},
                    "skill_lookup": ["helper"],
                    "body": "Beta",
                },
            },
        },
        {
            "schema_version": 1,
            "traits": {
                "alpha": {
                    "description": "New",
                    "order": None,
                    "config": {},
                    "skill_lookup": [],
                    "body": "New",
                }
            },
        },
    )
    selected = select_effective_documents(("alpha", "beta"), indexes)
    configured = apply_trait_config_overlays(
        selected,
        (
            LayerConfig(traits_config={"beta": {"nested": {"second": 2}}}),
            LayerConfig(traits_config={"inactive": {"ignored": True}}),
        ),
    )
    ordered = order_effective_traits(configured, ("alpha", "beta"))

    assert [document.name for document in ordered] == ["beta", "alpha"]
    assert ordered[0].config == {"nested": {"second": 2}, "keep": True}
    assert ordered[1].description == "New" and ordered[1].order is None
