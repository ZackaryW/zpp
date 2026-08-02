from __future__ import annotations

from collections.abc import Sequence

from zpp.utils.codespace_models import CodespaceMember


def writable_members(
    members: Sequence[CodespaceMember],
) -> tuple[CodespaceMember, ...]:
    return tuple(member for member in members if member.access == "writable")


def read_only_members(
    members: Sequence[CodespaceMember],
) -> tuple[CodespaceMember, ...]:
    return tuple(member for member in members if member.access == "read_only")
