from __future__ import annotations

from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    RootModel,
    ValidationError,
    model_validator,
)

from zpp.utils.models import (
    CacheWatch,
    LayerConfig,
    SavedIndex,
    TriggerRule,
    ValidationIssue,
    ZppValidationError,
)


NonEmptyString = Annotated[str, Field(min_length=1)]


class _TriggerRule(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    trait: NonEmptyString
    which: NonEmptyString | None = None
    workspace_contain: Annotated[list[NonEmptyString], Field(min_length=1)] | None = None

    @model_validator(mode="after")
    def has_at_most_one_condition(self) -> "_TriggerRule":
        null_conditions = self.model_fields_set.intersection(
            {"which", "workspace_contain"}
        ) - {
            name
            for name, value in (
                ("which", self.which),
                ("workspace_contain", self.workspace_contain),
            )
            if value is not None
        }
        if null_conditions:
            raise ValueError("an authored trigger condition cannot be null")
        if self.which is not None and self.workspace_contain is not None:
            raise ValueError("trigger rule may contain at most one condition")
        return self


class _TriggerConfig(RootModel[list[_TriggerRule]]):
    model_config = ConfigDict(strict=True)


class _LayerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    trait_overwrites: bool = False
    traits_config: dict[NonEmptyString, dict[str, JsonValue]] = Field(
        default_factory=dict,
        alias="traitsConfig",
    )


class _SavedIndex(RootModel[dict[NonEmptyString, NonEmptyString]]):
    model_config = ConfigDict(strict=True)


class _CacheWatch(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    cache_mtime_ns: Annotated[int, Field(ge=0)]


def validate_trigger_config(value: object) -> tuple[TriggerRule, ...]:
    parsed = _validate(_TriggerConfig, value)
    return tuple(
        TriggerRule(
            trait=rule.trait,
            which=rule.which,
            workspace_contain=(
                tuple(rule.workspace_contain)
                if rule.workspace_contain is not None
                else None
            ),
        )
        for rule in parsed.root
    )


def validate_layer_config(value: object) -> LayerConfig:
    parsed = _validate(_LayerConfig, value)
    return LayerConfig(
        trait_overwrites=parsed.trait_overwrites,
        traits_config=parsed.traits_config,
    )


def validate_saved_index(value: object) -> SavedIndex:
    parsed = _validate(_SavedIndex, value)
    return SavedIndex(bindings=parsed.root)


def validate_cache_watch(value: object) -> CacheWatch:
    parsed = _validate(_CacheWatch, value)
    return CacheWatch(cache_mtime_ns=parsed.cache_mtime_ns)


def _validate(model: type[BaseModel], value: object) -> Any:
    try:
        return model.model_validate(value, strict=True)
    except ValidationError as error:
        raise ZppValidationError(
            tuple(
                ValidationIssue(location=tuple(issue["loc"]), message=issue["msg"])
                for issue in error.errors()
            )
        ) from error
