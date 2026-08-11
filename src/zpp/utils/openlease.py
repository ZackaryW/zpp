from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Protocol

from openlease import (
    ConfigurationLayout,
    ExtensionDocumentBinding,
    ExtensionManifest,
    ExtensionRegistration,
    OpenLease,
    WriteDisposition,
    to_plain_managed_value,
)

from zpp.core.application import (
    BoundTraitDocument,
    BoundTraitSource,
)
from zpp.core.models import SourceKind

_EXTENSION_ID = "zpp.traits"
_FAMILY = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


def create_trait_documents(state_root: Path) -> OpenLeaseTraitDocuments:
    lifecycle = OpenLease(
        state_root,
        extensions=(ExtensionRegistration(ExtensionManifest(_EXTENSION_ID)),),
    )
    return OpenLeaseTraitDocuments(lifecycle)


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
    def bind_extension_document(
        self, binding: ExtensionDocumentBinding
    ) -> _Bound: ...

    def initialize_extension_document(
        self,
        binding: ExtensionDocumentBinding,
        *,
        initial: Mapping[str, object],
        boundary: Path | None = None,
        create_parents: bool = False,
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
