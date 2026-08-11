from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Protocol

from openlease import (
    CallbackEvent,
    CallbackMode,
    ConfigurationLayout,
    ConfigurationTarget,
    DirectDocumentTarget,
    ExtensionCallback,
    ExtensionDocumentBinding,
    ExtensionInvocation,
    ExtensionManifest,
    ExtensionOperation,
    ExtensionRegistration,
    OpenLease,
    WriteDisposition,
    to_plain_managed_value,
)
from openlease.utils.git_adapter import GitAdapter
from openlease.utils.processes import ProcessRunner, SubprocessRunner

from zpp.core.application import (
    BoundTraitDocument,
    BoundTraitSource,
)
from zpp.core.behavior import (
    BehaviorAdapterRegistry,
    BehaviorExecutionError,
    BehaviorExecutionReport,
    BehaviorInitializationReport,
    BehaviorProviderAdapter,
    BehaviorRunInput,
    parse_behavior_mapping,
    select_behavior_targets,
)
from zpp.core.models import SourceKind
from zpp.utils.behavior_providers import default_behavior_adapters

_EXTENSION_ID = "zpp.traits"
_BEHAVIOR_EXTENSION_ID = "zpp.behave"
_FAMILY = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


def create_trait_documents(state_root: Path) -> OpenLeaseTraitDocuments:
    lifecycle = OpenLease(
        state_root,
        extensions=(ExtensionRegistration(ExtensionManifest(_EXTENSION_ID)),),
    )
    return OpenLeaseTraitDocuments(lifecycle)


def create_zpp_openlease(
    state_root: Path,
    *,
    behavior_adapters: Sequence[BehaviorProviderAdapter] | None = None,
    behavior_git: GitAdapter | None = None,
    behavior_runner: ProcessRunner | None = None,
) -> OpenLease:
    return OpenLease(
        state_root,
        extensions=(
            ExtensionRegistration(ExtensionManifest(_EXTENSION_ID)),
            behavior_extension(
                behavior_adapters,
                git=behavior_git,
                runner=behavior_runner,
                state_root=state_root,
            ),
        ),
    )


def behavior_extension(
    adapters: Sequence[BehaviorProviderAdapter] | None = None,
    *,
    git: GitAdapter | None = None,
    runner: ProcessRunner | None = None,
    state_root: Path | None = None,
) -> ExtensionRegistration:
    selected = tuple(
        default_behavior_adapters(runner) if adapters is None else adapters
    )

    def validate(configuration: Mapping[str, object]) -> None:
        plain = to_plain_managed_value(configuration)
        if not isinstance(plain, dict):
            raise ValueError("behavior configuration is not a mapping")
        parse_behavior_mapping(
            plain,
            registry=BehaviorAdapterRegistry(selected),
        )

    def initialize(invocation: ExtensionInvocation) -> object:
        return _initialize_behavior_invocation(invocation, selected)

    def run(invocation: ExtensionInvocation) -> object:
        return _run_behavior_invocation(
            invocation,
            selected,
            git=git,
            runner=runner,
            state_root=state_root,
        )

    return ExtensionRegistration(
        manifest=ExtensionManifest(_BEHAVIOR_EXTENSION_ID),
        operations=(
            ExtensionOperation("initialize", initialize, target_kinds=("direct",)),
            ExtensionOperation(
                "run", run, target_kinds=("direct", "repository", "cohort")
            ),
        ),
        callbacks=(
            ExtensionCallback(
                CallbackEvent.RECONCILE_BEFORE_REPOSITORY,
                "run",
                (CallbackMode.GATE, CallbackMode.OBSERVE),
            ),
            ExtensionCallback(
                CallbackEvent.RECONCILE_AFTER_REPOSITORY,
                "run",
                (CallbackMode.OBSERVE,),
            ),
            ExtensionCallback(
                CallbackEvent.RECONCILE_AFTER_COHORT,
                "run",
                (CallbackMode.OBSERVE,),
            ),
        ),
        validator=validate,
    )


def _initialize_behavior_invocation(
    invocation: ExtensionInvocation,
    adapters: Sequence[BehaviorProviderAdapter],
) -> object:
    root = _behavior_repository_root(invocation)
    mapping = parse_behavior_mapping(
        _plain_behavior_configuration(invocation),
        registry=BehaviorAdapterRegistry(adapters),
    )
    from zpp.utils.behavior_providers import behavior_provider_diagnostics

    return BehaviorInitializationReport(
        root,
        tuple(mapping.commands),
        behavior_provider_diagnostics(root),
    )


def _run_behavior_invocation(
    invocation: ExtensionInvocation,
    adapters: Sequence[BehaviorProviderAdapter],
    *,
    git: GitAdapter | None,
    runner: ProcessRunner | None,
    state_root: Path | None,
) -> object:
    if invocation.event is not None and (
        not isinstance(invocation.input, Mapping)
        or "complete" not in invocation.input
    ):
        raise BehaviorExecutionError(
            "behavior callback requires an explicit complete or affected selection mode"
        )
    request = _behavior_run_input(invocation.input)
    root = _behavior_repository_root(invocation)
    process_runner = runner or SubprocessRunner()
    selected = tuple(adapters)
    if invocation.event is None:
        configuration = _plain_behavior_configuration(invocation)
    else:
        if state_root is None:
            raise BehaviorExecutionError(
                "callback behavior requires the selected OpenLease state root"
            )
        callback_host = OpenLease(
            state_root,
            extensions=(
                behavior_extension(
                    selected,
                    git=git,
                    runner=process_runner,
                    state_root=state_root,
                ),
            ),
        )
        bound = callback_host.bind_extension_document(
            ExtensionDocumentBinding(
                extension_id=_BEHAVIOR_EXTENSION_ID,
                path=root / "zpp.behave.yaml",
                codec="yaml",
                layout=ConfigurationLayout.DEDICATED,
                repository_path=root,
            )
        )
        plain = to_plain_managed_value(bound.config.snapshot())
        if not isinstance(plain, dict):
            raise BehaviorExecutionError("behavior configuration is not a mapping")
        configuration = plain
    mapping = parse_behavior_mapping(
        configuration,
        registry=BehaviorAdapterRegistry(selected),
    )
    command = mapping.commands.get(request.command)
    if command is None:
        raise BehaviorExecutionError(
            f"behavior command is not declared: {request.command}"
        )
    changed_paths: tuple[str, ...] = ()
    if not (request.complete or request.targets or request.gate is not None):
        git_adapter = git or GitAdapter()
        checkout = git_adapter.inspect(root)
        changed = (
            git_adapter.worktree_changed_paths(checkout, checkout.head)
            if request.base is None
            else git_adapter.changed_paths(checkout, request.base, request.head or "")
        )
        changed_paths = tuple(item.path for item in changed)
    targets = select_behavior_targets(
        command,
        request,
        changed_paths=changed_paths,
    )
    if not targets:
        return BehaviorExecutionReport(root, request.command, (), None)
    values = tuple(target.value for target in targets)
    arguments = command.provider.adapter.argv(root, command.provider.settings, values)
    if not arguments or not arguments[0]:
        raise BehaviorExecutionError("behavior adapter returned an empty executable")
    result = process_runner.run(tuple(arguments), cwd=root)
    return BehaviorExecutionReport(root, request.command, targets, result)


def _plain_behavior_configuration(
    invocation: ExtensionInvocation,
) -> Mapping[str, object]:
    plain = to_plain_managed_value(invocation.config.snapshot())
    if not isinstance(plain, dict):
        raise ValueError("behavior configuration is not a mapping")
    return plain


def _behavior_repository_root(invocation: ExtensionInvocation) -> Path:
    target = invocation.context.target
    if isinstance(target, DirectDocumentTarget):
        return (target.repository_path or target.path.parent).resolve()
    if isinstance(target, ConfigurationTarget):
        repository_id = (
            invocation.event.repository_id
            if invocation.event is not None
            and invocation.event.repository_id is not None
            else target.identifier
        )
        member = next(
            (
                member
                for member in invocation.context.members
                if member.repository_id == repository_id
            ),
            None,
        )
        if member is not None:
            return member.effective_path.resolve()
    raise ValueError("OpenLease did not supply an exact repository target")


def _behavior_run_input(value: object) -> BehaviorRunInput:
    if isinstance(value, BehaviorRunInput):
        request = value
    elif isinstance(value, Mapping):
        allowed = {"command", "complete", "base", "head", "targets", "gate"}
        unknown = set(value).difference(allowed)
        if unknown:
            raise BehaviorExecutionError(
                "unknown behavior run input: " + ", ".join(sorted(unknown))
            )
        targets = value.get("targets", ())
        if isinstance(targets, str) or not isinstance(targets, Sequence):
            raise BehaviorExecutionError("behavior targets must be a sequence")
        request = BehaviorRunInput(
            command=value.get("command"),  # type: ignore[arg-type]
            complete=value.get("complete", False),  # type: ignore[arg-type]
            base=value.get("base"),  # type: ignore[arg-type]
            head=value.get("head"),  # type: ignore[arg-type]
            targets=tuple(targets),
            gate=value.get("gate"),  # type: ignore[arg-type]
        )
    else:
        raise BehaviorExecutionError("behavior run input is invalid")
    if not isinstance(request.command, str) or not request.command:
        raise BehaviorExecutionError("behavior run input requires a command")
    if not isinstance(request.complete, bool):
        raise BehaviorExecutionError("behavior complete mode must be boolean")
    if request.base is not None and not isinstance(request.base, str):
        raise BehaviorExecutionError("behavior base must be a string")
    if request.head is not None and not isinstance(request.head, str):
        raise BehaviorExecutionError("behavior head must be a string")
    if any(not isinstance(item, str) or not item for item in request.targets):
        raise BehaviorExecutionError(
            "behavior target identities must be non-empty strings"
        )
    if request.gate is not None and (
        not isinstance(request.gate, str) or not request.gate
    ):
        raise BehaviorExecutionError(
            "behavior gate identity must be a non-empty string"
        )
    return request


class OpenLeaseBehaviorDocuments:
    def __init__(self, lifecycle: OpenLease | _OpenLeasePort) -> None:
        self._lifecycle = lifecycle

    def initialize(self, repository: Path) -> BehaviorInitializationReport:
        root = repository.resolve()
        path = root / "zpp.behave.yaml"
        if path.is_file():
            bound = self._lifecycle.bind_extension_document(
                self._binding(root, writable=False)
            )
        else:
            bound = self._lifecycle.initialize_extension_document(
                self._binding(root, writable=True),
                initial={"version": 1, "commands": {}},
                boundary=root,
                create_parents=False,
            )
        result = bound.invoke("initialize")
        if not isinstance(result.value, BehaviorInitializationReport):
            raise ValueError("behavior initialization returned an invalid report")
        return result.value

    def run(
        self,
        repository: Path,
        request: BehaviorRunInput,
    ) -> BehaviorExecutionReport:
        root = repository.resolve()
        bound = self._lifecycle.bind_extension_document(
            self._binding(root, writable=False)
        )
        result = bound.invoke("run", request)
        if result.value is None:
            diagnostic = getattr(result.outcome, "diagnostic", None)
            raise BehaviorExecutionError(diagnostic or "behavior execution failed")
        if not isinstance(result.value, BehaviorExecutionReport):
            raise ValueError("behavior execution returned an invalid report")
        return result.value

    @staticmethod
    def _binding(repository: Path, *, writable: bool) -> ExtensionDocumentBinding:
        return ExtensionDocumentBinding(
            extension_id=_BEHAVIOR_EXTENSION_ID,
            path=repository / "zpp.behave.yaml",
            codec="yaml",
            layout=ConfigurationLayout.DEDICATED,
            writable=writable,
            repository_path=repository,
        )


@dataclass(frozen=True, slots=True)
class ManagedTraitDocument:
    path: Path
    family: str | None
    values: Mapping[str, object]
    provenance: object


@dataclass(frozen=True, slots=True)
class BoundRepositoryTraits:
    context: BoundTraitDocument | None
    source: BoundTraitSource


class _Configuration(Protocol):
    def snapshot(self) -> Mapping[str, object]: ...
    def snapshot_record(self) -> object: ...
    def set(self, key: str, value: object) -> WriteDisposition: ...


class _Bound(Protocol):
    config: _Configuration


class _OpenLeasePort(Protocol):
    def bind_extension_document(self, binding: ExtensionDocumentBinding) -> _Bound: ...

    def initialize_extension_document(
        self,
        binding: ExtensionDocumentBinding,
        *,
        initial: Mapping[str, object],
        boundary: Path | None = None,
        create_parents: bool = False,
    ) -> _Bound: ...

    def snapshot(self) -> object: ...

    def bind_extension(
        self,
        extension_id: str,
        space_id: str,
        target: ConfigurationTarget,
    ) -> _Bound: ...


class TraitDocumentPort(Protocol):
    def read_context(self, repository: Path) -> ManagedTraitDocument | None: ...
    def read_traits(self, repository: Path) -> Sequence[ManagedTraitDocument]: ...
    def initialize_trait(
        self,
        repository: Path,
        family: str,
        initial: Mapping[str, object],
    ) -> ManagedTraitDocument: ...
    def set_trait_value(
        self,
        repository: Path,
        family: str,
        key: str,
        value: object,
    ) -> WriteDisposition: ...


class OpenLeaseTraitDocuments:
    def __init__(self, lifecycle: OpenLease | _OpenLeasePort) -> None:
        self._lifecycle = lifecycle

    def read_context(self, repository: Path) -> ManagedTraitDocument | None:
        root = repository.resolve()
        path = root / ".zpp" / "zpp.toml"
        if not path.is_file():
            return None
        return self._read(path, root, family=None)

    def read_repository(self, repository: Path) -> BoundRepositoryTraits:
        root = repository.resolve()
        context = self.read_context(root)
        traits = self.read_traits(root)
        return BoundRepositoryTraits(
            context=(
                BoundTraitDocument(
                    family="context",
                    values=context.values,
                    identifier=str(context.path),
                    path=context.path,
                )
                if context is not None
                else None
            ),
            source=BoundTraitSource(
                kind=SourceKind.REPOSITORY,
                identifier=str(root),
                order=0,
                documents=tuple(
                    BoundTraitDocument(
                        family=document.family or "",
                        values=document.values,
                        identifier=str(document.path),
                        order=order,
                        path=document.path,
                    )
                    for order, document in enumerate(traits)
                    if document.family is not None
                ),
            ),
        )

    def read_traits(self, repository: Path) -> tuple[ManagedTraitDocument, ...]:
        root = repository.resolve()
        trait_root = root / ".zpp" / "traits"
        if not trait_root.is_dir():
            return ()
        documents: list[ManagedTraitDocument] = []
        for path in sorted(trait_root.glob("*.toml")):
            resolved = path.resolve()
            if not resolved.is_relative_to(trait_root.resolve()):
                raise ValueError(f"trait document escapes repository: {path}")
            documents.append(self._read(resolved, root, family=path.stem))
        return tuple(documents)

    def read_space_sources(
        self,
        repository: Path,
        space_id: str,
        *,
        authority: str | None = None,
    ) -> tuple[BoundTraitSource, ...]:
        root = repository.resolve()
        state = self._lifecycle.snapshot()
        repositories = getattr(state, "repositories", ())
        matching = tuple(
            item for item in repositories if Path(item.path).resolve() == root
        )
        if len(matching) != 1:
            raise ValueError(
                "selected-space traits require one registered repository matching "
                f"the target path: {root}"
            )
        target = (
            ConfigurationTarget.authority(authority)
            if authority is not None
            else ConfigurationTarget.repository(matching[0].identifier)
        )
        bound = self._lifecycle.bind_extension(_EXTENSION_ID, space_id, target)
        record = bound.config.snapshot_record()
        sources: list[BoundTraitSource] = []
        for position, binding in enumerate(record.bindings):
            path = Path(binding.canonical_path)
            values = to_plain_managed_value(binding.selected)
            if not isinstance(values, dict):
                raise ValueError(f"managed trait document is not a mapping: {path}")
            kind = self._source_kind(binding.scope_kind)
            identifier = f"openlease:{binding.identifier}"
            sources.append(
                BoundTraitSource(
                    kind=kind,
                    identifier=identifier,
                    order=binding.order,
                    documents=(
                        BoundTraitDocument(
                            family=path.stem,
                            values=MappingProxyType(values),
                            identifier=identifier,
                            order=position,
                            path=path,
                        ),
                    ),
                )
            )
        return tuple(sources)

    def initialize_trait(
        self,
        repository: Path,
        family: str,
        initial: Mapping[str, object],
    ) -> ManagedTraitDocument:
        root = repository.resolve()
        path = self._trait_path(root, family)
        binding = self._binding(path, root, writable=True)
        bound = self._lifecycle.initialize_extension_document(
            binding,
            initial=initial,
            boundary=root / ".zpp",
            create_parents=True,
        )
        return self._managed_document(path, family, bound)

    def initialize_context(self, repository: Path) -> ManagedTraitDocument:
        root = repository.resolve()
        path = root / ".zpp" / "zpp.toml"
        bound = self._lifecycle.initialize_extension_document(
            self._binding(path, root, writable=True),
            initial={"facet": {}},
            boundary=root / ".zpp",
            create_parents=True,
        )
        return self._managed_document(path, None, bound)

    def set_trait_value(
        self,
        repository: Path,
        family: str,
        key: str,
        value: object,
    ) -> WriteDisposition:
        root = repository.resolve()
        path = self._trait_path(root, family)
        bound = self._lifecycle.bind_extension_document(
            self._binding(path, root, writable=True)
        )
        return bound.config.set(key, value)

    def _read(
        self,
        path: Path,
        repository: Path,
        *,
        family: str | None,
    ) -> ManagedTraitDocument:
        bound = self._lifecycle.bind_extension_document(
            self._binding(path, repository, writable=False)
        )
        return self._managed_document(path, family, bound)

    @staticmethod
    def _binding(
        path: Path,
        repository: Path,
        *,
        writable: bool,
    ) -> ExtensionDocumentBinding:
        return ExtensionDocumentBinding(
            extension_id=_EXTENSION_ID,
            path=path,
            codec="toml",
            layout=ConfigurationLayout.DEDICATED,
            writable=writable,
            repository_path=repository,
        )

    @staticmethod
    def _managed_document(
        path: Path,
        family: str | None,
        bound: _Bound,
    ) -> ManagedTraitDocument:
        plain = to_plain_managed_value(bound.config.snapshot())
        if not isinstance(plain, dict):
            raise ValueError(f"managed trait document is not a mapping: {path}")
        return ManagedTraitDocument(
            path=path,
            family=family,
            values=MappingProxyType(plain),
            provenance=bound.config.snapshot_record(),
        )

    @staticmethod
    def _trait_path(repository: Path, family: str) -> Path:
        if not _FAMILY.fullmatch(family):
            raise ValueError(f"invalid trait family: {family}")
        return repository / ".zpp" / "traits" / f"{family}.toml"

    @staticmethod
    def _source_kind(scope_kind: str) -> SourceKind:
        if scope_kind in {"repository", "authority"}:
            return SourceKind.REPOSITORY
        if scope_kind == "space":
            return SourceKind.SPACE
        return SourceKind.GLOBAL
