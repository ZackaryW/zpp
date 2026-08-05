from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from yaml.constructor import ConstructorError

from zpp.utils.models import ManagedStateError


TARGET_MARKER = "{targets}"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class BehaviorTarget(_StrictModel):
    value: str = Field(min_length=1)
    paths: tuple[str, ...] = Field(min_length=1)

    @field_validator("paths")
    @classmethod
    def validate_paths(cls, paths: tuple[str, ...]) -> tuple[str, ...]:
        for pattern in paths:
            relative = PurePosixPath(pattern)
            if (
                not pattern
                or "\\" in pattern
                or relative.is_absolute()
                or ".." in relative.parts
                or pattern.count("[") != pattern.count("]")
            ):
                raise ValueError(f"invalid repository impact glob: {pattern}")
        return paths


class ArgvProvider(_StrictModel):
    kind: Literal["argv"] = "argv"
    argv: tuple[str, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def require_one_target_marker(self) -> ArgvProvider:
        if self.argv.count(TARGET_MARKER) != 1 or self.argv[0] == TARGET_MARKER:
            raise ValueError("argv provider requires exactly one target expansion position")
        if any(not value for value in self.argv):
            raise ValueError("argv provider values must not be empty")
        return self


class NxProvider(_StrictModel):
    kind: Literal["nx"] = "nx"
    target: str = Field(min_length=1)
    args: tuple[str, ...] = ()

    @field_validator("args")
    @classmethod
    def reject_target_marker(cls, args: tuple[str, ...]) -> tuple[str, ...]:
        if TARGET_MARKER in args or any(not value for value in args):
            raise ValueError("Nx provider arguments must be non-empty literal values")
        return args


BehaviorProvider = Annotated[ArgvProvider | NxProvider, Field(discriminator="kind")]


class BehaviorCommand(_StrictModel):
    provider: BehaviorProvider
    targets: dict[str, BehaviorTarget] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_target_values(self) -> BehaviorCommand:
        values = tuple(target.value for target in self.targets.values())
        if len(values) != len(set(values)):
            raise ValueError("behavior target values must be unique within a command")
        return self


class BehaviorMapping(_StrictModel):
    version: Literal[1]
    commands: dict[str, BehaviorCommand]


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as error:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from error
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_behavior_mapping(path: Path) -> BehaviorMapping:
    if path.is_symlink() or not path.is_file():
        raise ManagedStateError(f"behavior mapping is not a regular file: {path}")
    try:
        raw = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
        return BehaviorMapping.model_validate(raw)
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
        raise ManagedStateError(f"behavior mapping is invalid at {path}: {error}") from error


def dump_behavior_scaffold(path: Path) -> bool:
    if path.exists() or path.is_symlink():
        load_behavior_mapping(path)
        return False
    path.write_text("version: 1\ncommands: {}\n", encoding="utf-8")
    return True
