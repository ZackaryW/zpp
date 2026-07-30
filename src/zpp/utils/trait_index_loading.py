from __future__ import annotations

import json
from typing import Annotated, Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError

from zpp.utils.json_io import atomic_write_json
from zpp.utils.models import AuthoredLayerPaths, TraitCachePaths, TraitIndex
from zpp.utils.trait_cache import trait_cache_is_current, write_trait_cache_watchfile
from zpp.utils.trait_compiler import compile_trait_index


class _TraitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    description: Annotated[str, Field(min_length=1)]
    order: Annotated[int, Field(ge=0)] | None
    config: dict[str, JsonValue]
    skill_lookup: list[str]
    body: str


class _TraitIndex(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal[1]
    traits: dict[str, _TraitRecord]


def load_trait_index(
    authored: AuthoredLayerPaths,
    cache: TraitCachePaths,
) -> TraitIndex:
    if not authored.traits.is_dir():
        raise NotADirectoryError(authored.traits)

    if trait_cache_is_current(authored.traits, cache.index, cache.watch):
        try:
            return _validate_index(
                json.loads(cache.index.read_text(encoding="utf-8"))
            )
        except (OSError, UnicodeError, json.JSONDecodeError, ValidationError):
            pass

    index = compile_trait_index(sorted(authored.traits.glob("*.md")))
    cache.root.mkdir(parents=True, exist_ok=True)
    atomic_write_json(cache.index, index)
    write_trait_cache_watchfile(cache.index, cache.watch)
    return index


def _validate_index(value: Any) -> TraitIndex:
    model = _TraitIndex.model_validate(value, strict=True)
    return cast(TraitIndex, model.model_dump(mode="python"))
