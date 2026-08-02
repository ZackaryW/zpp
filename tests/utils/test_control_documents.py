import pytest

from zpp.utils.control_documents import (
    validate_cache_watch,
    validate_layer_config,
    validate_saved_index,
    validate_trigger_config,
)
from zpp.utils.models import ZppValidationError


def test_control_document_validators_normalize_the_accepted_shapes() -> None:
    triggers = validate_trigger_config(
        [
            {"trait": "always"},
            {"trait": "tooling", "which": "neutral-tool"},
            {
                "trait": "workspace",
                "workspace_contain": ["pyproject.toml", "src/**/*.py"],
            },
        ]
    )
    layer = validate_layer_config(
        {
            "trait_overwrites": True,
            "traitsConfig": {"always": {"enabled": False, "nested": {"值": 1}}},
        }
    )
    saved = validate_saved_index({"C:/work/one": "shared", "D:/two": "shared"})
    watch = validate_cache_watch({"cache_mtime_ns": 123})

    assert [trigger.trait for trigger in triggers] == ["always", "tooling", "workspace"]
    assert triggers[0].which is None and triggers[0].workspace_contain is None
    assert triggers[1].which == "neutral-tool" and triggers[1].workspace_contain is None
    assert triggers[2].which is None
    assert triggers[2].workspace_contain == ("pyproject.toml", "src/**/*.py")
    assert layer.trait_overwrites is True
    assert layer.traits_config == {"always": {"enabled": False, "nested": {"值": 1}}}
    assert saved.bindings == {"C:/work/one": "shared", "D:/two": "shared"}
    assert watch.cache_mtime_ns == 123


@pytest.mark.parametrize("condition", ["which", "workspace_contain"])
def test_trigger_condition_rejects_explicit_null(condition: str) -> None:
    with pytest.raises(ZppValidationError):
        validate_trigger_config([{"trait": "invalid", condition: None}])


@pytest.mark.parametrize(
    ("validator", "value"),
    [
        (
            validate_trigger_config,
            [
                {"trait": "compound", "which": "tool", "workspace_contain": ["*"]},
                {"trait": "extra", "unknown": True},
            ],
        ),
        (validate_layer_config, {"trait_overwrites": 1, "traitsConfig": []}),
        (validate_saved_index, {"C:/work": 1}),
        (validate_cache_watch, {"cache_mtime_ns": True, "unknown": 1}),
    ],
)
def test_control_document_validators_reject_non_contract_shapes(
    validator: object,
    value: object,
) -> None:
    with pytest.raises(ZppValidationError) as caught:
        validator(value)  # type: ignore[operator]

    assert caught.value.issues
