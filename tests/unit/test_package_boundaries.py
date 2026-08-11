from __future__ import annotations

from importlib.util import find_spec


def test_established_package_boundaries_replace_root_utility_surfaces() -> None:
    assert find_spec("zpp.core") is not None
    assert find_spec("zpp.utils") is not None
    assert find_spec("zpp.artifacts") is not None
    assert find_spec("zpp.models") is None
    assert find_spec("zpp.integrations") is None
