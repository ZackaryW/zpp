from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from zpp.utils.processes import ProcessResult
from zpp.utils.repository_paths import (
    RepositoryPathError,
    glob_full_match,
    normalize_repository_path,
    validate_repository_glob,
)


class BehaviorMappingError(ValueError):
    """A repository behavior mapping is invalid."""


class BehaviorProviderError(ValueError):
    """A configured behavior provider is invalid or unavailable."""


class BehaviorExecutionError(RuntimeError):
    """A requested behavior operation cannot be executed."""


class BehaviorProviderAdapter(Protocol):
    kind: str

    def validate(self, raw: Mapping[str, object]) -> object: ...

    def argv(
        self,
        root: Path,
        settings: object,
        targets: tuple[str, ...],
    ) -> tuple[str, ...]: ...


@dataclass(frozen=True, slots=True)
class ValidatedBehaviorProvider:
    adapter: BehaviorProviderAdapter
    settings: object

    @property
    def kind(self) -> str:
        return self.adapter.kind


class BehaviorAdapterRegistry:
    def __init__(self, adapters: Sequence[BehaviorProviderAdapter]) -> None:
        selected: dict[str, BehaviorProviderAdapter] = {}
        for adapter in adapters:
            kind = getattr(adapter, "kind", "")
            if not isinstance(kind, str) or not kind:
                raise BehaviorProviderError("adapter kind must be a non-empty string")
            if kind in selected:
                raise BehaviorProviderError(f"duplicate behavior adapter kind: {kind}")
            selected[kind] = adapter
        self._adapters = selected

    def validate(self, raw: Mapping[str, object]) -> ValidatedBehaviorProvider:
        kind = raw.get("kind")
        if not isinstance(kind, str) or not kind:
            raise BehaviorProviderError("behavior provider requires a non-empty kind")
        adapter = self._adapters.get(kind)
        if adapter is None:
            raise BehaviorProviderError(f"unknown behavior adapter: {kind}")
        return ValidatedBehaviorProvider(adapter, adapter.validate(raw))


@dataclass(frozen=True, slots=True)
class BehaviorTarget:
    name: str
    value: str
    paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BehaviorCommand:
    name: str
    provider: ValidatedBehaviorProvider
    targets: Mapping[str, BehaviorTarget]
    gates: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class BehaviorMapping:
    version: int
    commands: Mapping[str, BehaviorCommand]


@dataclass(frozen=True, slots=True)
class BehaviorRunInput:
    command: str
    complete: bool = False
    base: str | None = None
    head: str | None = None
    targets: tuple[str, ...] = ()
    gate: str | None = None


@dataclass(frozen=True, slots=True)
class BehaviorInitializationReport:
    root: Path
    commands: tuple[str, ...]
    provider_diagnostics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BehaviorExecutionReport:
    root: Path
    command: str
    targets: tuple[BehaviorTarget, ...]
    result: ProcessResult | None


NonEmptyString = Annotated[str, Field(min_length=1)]


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class _RawTarget(_ClosedModel):
    value: NonEmptyString
    paths: list[NonEmptyString] = Field(min_length=1)


class _RawCommand(_ClosedModel):
    provider: dict[str, Any]
    targets: dict[NonEmptyString, _RawTarget] = Field(min_length=1)
    gates: dict[
        NonEmptyString,
        Annotated[list[NonEmptyString], Field(min_length=1)],
    ] = Field(default_factory=dict)


class _RawMapping(_ClosedModel):
    version: int
    commands: dict[NonEmptyString, _RawCommand]


def parse_behavior_mapping(
    configuration: Mapping[str, object],
    *,
    registry: BehaviorAdapterRegistry,
) -> BehaviorMapping:
    try:
        raw = _RawMapping.model_validate(dict(configuration), strict=True)
        if raw.version != 1:
            raise ValueError("behavior mapping version must be 1")
        commands: dict[str, BehaviorCommand] = {}
        for name, command in raw.commands.items():
            provider = registry.validate(command.provider)
            targets: dict[str, BehaviorTarget] = {}
            values: set[str] = set()
            for target_name, target in command.targets.items():
                if target.value in values:
                    raise ValueError(
                        "behavior target values must be unique within a command"
                    )
                values.add(target.value)
                targets[target_name] = BehaviorTarget(
                    target_name,
                    target.value,
                    tuple(validate_repository_glob(item) for item in target.paths),
                )
            gates: dict[str, tuple[str, ...]] = {}
            for gate_name, gate_targets in command.gates.items():
                requested = set(gate_targets)
                if len(requested) != len(gate_targets):
                    raise ValueError(f"behavior gate repeats a target: {gate_name}")
                unknown = requested.difference(targets)
                if unknown:
                    raise ValueError(
                        f"behavior gate {gate_name} refers to undeclared targets: "
                        + ", ".join(sorted(unknown))
                    )
                gates[gate_name] = tuple(
                    target_name for target_name in targets if target_name in requested
                )
            commands[name] = BehaviorCommand(
                name,
                provider,
                MappingProxyType(targets),
                MappingProxyType(gates),
            )
        return BehaviorMapping(raw.version, MappingProxyType(commands))
    except (
        ValidationError,
        TypeError,
        ValueError,
        BehaviorProviderError,
        RepositoryPathError,
    ) as error:
        if isinstance(error, BehaviorMappingError):
            raise
        raise BehaviorMappingError(str(error)) from error


def select_affected_targets(
    command: BehaviorCommand,
    changed_paths: Sequence[str],
) -> tuple[BehaviorTarget, ...]:
    if not changed_paths:
        return ()
    matched: set[str] = set()
    for value in changed_paths:
        try:
            path = normalize_repository_path(value).as_posix()
        except RepositoryPathError:
            return tuple(command.targets.values())
        names = {
            name
            for name, target in command.targets.items()
            if any(glob_full_match(path, pattern) for pattern in target.paths)
        }
        if not names:
            return tuple(command.targets.values())
        matched.update(names)
    return tuple(target for name, target in command.targets.items() if name in matched)


def select_behavior_targets(
    command: BehaviorCommand,
    request: BehaviorRunInput,
    *,
    changed_paths: Sequence[str] = (),
) -> tuple[BehaviorTarget, ...]:
    if (request.base is None) != (request.head is None):
        raise BehaviorExecutionError("base and head must be supplied together")
    revision = request.base is not None
    if (
        sum(
            (
                request.complete,
                bool(request.targets),
                request.gate is not None,
                revision,
            )
        )
        > 1
    ):
        raise BehaviorExecutionError("behavior selection modes are mutually exclusive")
    if request.targets:
        requested = set(request.targets)
        unknown = requested.difference(command.targets)
        if unknown:
            raise BehaviorExecutionError(
                "behavior targets are not declared: " + ", ".join(sorted(unknown))
            )
        return tuple(
            target for name, target in command.targets.items() if name in requested
        )
    if request.gate is not None:
        gate_targets = command.gates.get(request.gate)
        if gate_targets is None:
            raise BehaviorExecutionError(
                f"behavior gate is not declared: {request.gate}"
            )
        return tuple(command.targets[name] for name in gate_targets)
    if request.complete:
        return tuple(command.targets.values())
    return select_affected_targets(command, changed_paths)
