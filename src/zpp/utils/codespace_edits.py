from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from zpp.utils.codespace_identity import checkout_claim_key
from zpp.utils.git_layers import GitCheckout, inspect_git_checkout


EditAction = Literal["add", "add_read_only", "remove", "promote", "demote"]


@dataclass(frozen=True, slots=True)
class CodespaceEditTarget:
    action: EditAction
    path: Path
    checkout: GitCheckout
    checkout_key: str


@dataclass(frozen=True, slots=True)
class CodespaceEditOperations:
    targets: tuple[CodespaceEditTarget, ...]

    def keys(self, action: EditAction) -> frozenset[str]:
        return frozenset(
            target.checkout_key for target in self.targets if target.action == action
        )


def normalize_codespace_edit(
    *,
    add: Sequence[Path],
    add_read_only: Sequence[Path],
    remove: Sequence[Path],
    promote: Sequence[Path],
    demote: Sequence[Path],
) -> CodespaceEditOperations:
    requested = (
        ("add", add),
        ("add_read_only", add_read_only),
        ("remove", remove),
        ("promote", promote),
        ("demote", demote),
    )
    targets: list[CodespaceEditTarget] = []
    actions_by_key: dict[str, EditAction] = {}
    for action, paths in requested:
        for path in paths:
            checkout = inspect_git_checkout(path)
            key = checkout_claim_key(checkout)
            previous = actions_by_key.get(key)
            if previous is not None:
                raise ValueError(
                    f"contradictory edit operations for {checkout.root}: "
                    f"{previous} and {action}"
                )
            actions_by_key[key] = action
            targets.append(
                CodespaceEditTarget(
                    action=action,
                    path=checkout.root,
                    checkout=checkout,
                    checkout_key=key,
                )
            )
    return CodespaceEditOperations(tuple(targets))
