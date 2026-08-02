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
    source_checkout_key: str = Field(min_length=1)
    commit: str = Field(min_length=1)
    kind: Literal["project", "store"]
    store_id: str | None = None
    access: Literal["writable", "read_only"] = "writable"
    generated_worktree: bool = False
    branch: str | None = None

    @model_validator(mode="before")
    @classmethod
    def default_source_to_effective(cls, value: object) -> object:
        if isinstance(value, dict) and "source_checkout_key" not in value:
            return {**value, "source_checkout_key": value.get("checkout_key")}
        return value


class CodespaceProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    generation: int = Field(ge=1)
    structure_key: str = Field(min_length=1)


class CodespaceClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str = Field(min_length=1)
    snapshot_key: str = Field(min_length=1)
    members: tuple[CodespaceMember, ...]
    projection: CodespaceProjection | None = None

    @model_validator(mode="after")
    def checkout_keys_are_unique(self) -> "CodespaceClaim":
        keys = [member.checkout_key for member in self.members]
        if len(keys) != len(set(keys)):
            raise ValueError("claim contains duplicate physical checkouts")
        return self


class ReleasedCheckoutDebt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    original_path: Path
    effective_path: Path
    checkout_key: str = Field(min_length=1)
    branch: str = Field(min_length=1)
    worktree_removed: bool = False
    branch_disposition: Literal["pending", "reconciled", "abandoned"] = "pending"


class ReleasedCodespace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: str = Field(min_length=1)
    debts: tuple[ReleasedCheckoutDebt, ...] = ()

    @model_validator(mode="after")
    def debt_keys_are_unique(self) -> "ReleasedCodespace":
        keys = [debt.checkout_key for debt in self.debts]
        if len(keys) != len(set(keys)):
            raise ValueError("released codespace contains duplicate checkout debts")
        return self


class CodespaceIndex(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[3] = 3
    claims: dict[str, CodespaceClaim] = Field(default_factory=dict)
    released: dict[str, ReleasedCodespace] = Field(default_factory=dict)

    @model_validator(mode="after")
    def claim_keys_match_instance_ids(self) -> "CodespaceIndex":
        if any(key != claim.instance_id for key, claim in self.claims.items()):
            raise ValueError("claim key does not match its instance id")
        if any(
            key != released.instance_id
            for key, released in self.released.items()
        ):
            raise ValueError("released key does not match its instance id")
        checkout_keys = [
            member.checkout_key
            for claim in self.claims.values()
            for member in claim.members
            if member.access == "writable"
        ]
        if len(checkout_keys) != len(set(checkout_keys)):
            raise ValueError("physical checkout belongs to multiple claims")
        return self
