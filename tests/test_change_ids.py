import pytest

from zpp.core import change_ids


def test_date_addressed_change_id_is_accepted():
    assert change_ids.validate("c260724-isolate-workset-governance") == (
        "c260724-isolate-workset-governance"
    )


def test_numeric_leading_id_has_actionable_normalization():
    with pytest.raises(change_ids.ChangeIdError, match="c260724-my-change"):
        change_ids.validate("260724-my-change")


@pytest.mark.parametrize(
    "value",
    ["c260724", "c260724-", "c260724-Upper", "change-2026-07-24-name"],
)
def test_other_shapes_are_rejected(value):
    with pytest.raises(change_ids.ChangeIdError):
        change_ids.validate(value)
