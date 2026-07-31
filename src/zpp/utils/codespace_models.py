from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CodespaceMember(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    original_path: Path
    effective_path: Path
    checkout_key: str = Field(min_length=1)
    commit: str = Field(min_length=1)
    kind: Literal["project", "store"]
    store_id: str | None = None
    role: Literal["governing", "reference"] = "governing"
    generated_worktree: bool = False
    branch: str | None = None


class CodespaceClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str = Field(min_length=1)
    snapshot_key: str = Field(min_length=1)
    workset_name: str = Field(min_length=1)
    members: tuple[CodespaceMember, ...]
    workset_owned: bool = True

    @model_validator(mode="after")
    def checkout_keys_are_unique(self) -> "CodespaceClaim":
        keys = [member.checkout_key for member in self.members]
        if len(keys) != len(set(keys)):
            raise ValueError("claim contains duplicate physical checkouts")
        return self


class ReleasedCodespace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    claim: CodespaceClaim
    removed_worktree_keys: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def removed_keys_are_owned_generated_worktrees(self) -> "ReleasedCodespace":
        generated = {
            member.checkout_key
            for member in self.claim.members
            if member.generated_worktree
        }
        if not self.removed_worktree_keys <= generated:
            raise ValueError("removed key is not an owned generated worktree")
        return self


class CodespaceIndex(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    claims: dict[str, CodespaceClaim] = Field(default_factory=dict)
    released: dict[str, ReleasedCodespace] = Field(default_factory=dict)

    @model_validator(mode="after")
    def claim_keys_match_instance_ids(self) -> "CodespaceIndex":
        if any(key != claim.instance_id for key, claim in self.claims.items()):
            raise ValueError("claim key does not match its instance id")
        if any(
            key != released.claim.instance_id
            for key, released in self.released.items()
        ):
            raise ValueError("released key does not match its instance id")
        checkout_keys = [
            member.checkout_key
            for claim in self.claims.values()
            for member in claim.members
        ]
        if len(checkout_keys) != len(set(checkout_keys)):
            raise ValueError("physical checkout belongs to multiple claims")
        return self
