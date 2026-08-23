from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from uuid import UUID

import tomli_w
from openspec_bundler import (
    AcquisitionResult,
    AttachmentService,
    AuditResult,
    ChangeMember,
    LeaseBundle,
    LeaseCoordinator,
    LeaseStateRepository,
    OpenSpecStoreProvider,
)
from openspec_bundler.leases.discovery import RegisteredStoreProvider

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind
from zpp.utils.product_home import ZppHome

_REPOSITORY_EXTENSION = "zpp-traits"
_STORE_EXTENSION = "zpp-traits"
_FAMILY = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


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


class BundlerDocuments:
    def __init__(self, stores: RegisteredStoreProvider | None = None) -> None:
        self._stores = stores or OpenSpecStoreProvider()
        self._attachments = AttachmentService(self._stores)

    def read_repository(self, repository: Path) -> BoundRepositoryTraits:
        target = self._attachments.repository_from_path(repository)
        root = target.root
        context = self._read_toml(target, Path(".zpp/zpp.toml"), family=None)
        trait_root = root / ".zpp" / "traits"
        traits = (
            () if not trait_root.is_dir() else tuple(sorted(trait_root.glob("*.toml")))
        )
        documents = tuple(
            self._read_toml(target, path.relative_to(root), family=path.stem)
            for path in traits
        )
        return BoundRepositoryTraits(
            context=(
                None
                if context is None
                else BoundTraitDocument(
                    "context",
                    context.values,
                    identifier=str(context.path),
                    path=context.path,
                )
            ),
            source=BoundTraitSource(
                SourceKind.REPOSITORY,
                str(root),
                0,
                tuple(
                    BoundTraitDocument(
                        item.family or "",
                        item.values,
                        identifier=str(item.path),
                        order=position,
                        path=item.path,
                    )
                    for position, item in enumerate(documents)
                    if item is not None
                ),
            ),
        )

    def read_store_chain(self, target: Path) -> tuple[BoundTraitSource, ...]:
        topology = LeaseCoordinator(self._stores).discover_topology()
        selected = []
        resolved = target.resolve()
        for store in topology.stores:
            try:
                resolved.relative_to(store.root.resolve())
            except ValueError:
                continue
            selected.append(store)
        if not selected:
            return ()
        current = max(selected, key=lambda store: len(store.root.resolve().parts))
        chain = []
        while True:
            chain.append(current)
            if current.parent_uuid is None:
                break
            current = topology.by_uuid(current.parent_uuid)
        sources = []
        for order, store in enumerate(reversed(chain), start=1):
            attachment = self._attachments.read_store(
                store.store_uuid, _STORE_EXTENSION
            )
            if attachment is None:
                continue
            values = MappingProxyType(dict(attachment.values))
            raw_traits = values.get("traits")
            if isinstance(raw_traits, Mapping):
                documents = tuple(
                    BoundTraitDocument(
                        str(family),
                        MappingProxyType(dict(document)),
                        identifier=f"store:{store.store_uuid}:{family}",
                        order=position,
                        path=attachment.manifest_path,
                    )
                    for position, (family, document) in enumerate(raw_traits.items())
                    if isinstance(document, Mapping)
                )
            else:
                documents = (
                    BoundTraitDocument(
                        _STORE_EXTENSION,
                        values,
                        identifier=f"store:{store.store_uuid}",
                        path=attachment.manifest_path,
                    ),
                )
            sources.append(
                BoundTraitSource(
                    SourceKind.STORE,
                    f"store:{store.store_uuid}",
                    order,
                    documents,
                )
            )
        return tuple(sources)

    def initialize_context(self, repository: Path) -> ManagedTraitDocument:
        return self._initialize_toml(
            repository, Path(".zpp/zpp.toml"), None, {"facet": {}}
        )

    def initialize_trait(
        self, repository: Path, family: str, initial: Mapping[str, object]
    ) -> ManagedTraitDocument:
        if _FAMILY.fullmatch(family) is None:
            raise ValueError(f"invalid trait family: {family}")
        return self._initialize_toml(
            repository, Path(".zpp/traits") / f"{family}.toml", family, initial
        )

    def _read_toml(self, target, relative: Path, *, family: str | None):
        attachment = self._attachments.read_repository(
            target, _REPOSITORY_EXTENSION, relative
        )
        if attachment is None:
            return None
        values = tomllib.loads(attachment.content.decode("utf-8"))
        return ManagedTraitDocument(
            attachment.path,
            family,
            MappingProxyType(values),
            attachment,
        )

    def _initialize_toml(
        self,
        repository: Path,
        relative: Path,
        family: str | None,
        initial: Mapping[str, object],
    ) -> ManagedTraitDocument:
        target = self._attachments.repository_from_path(repository)
        attachment = self._attachments.initialize_repository(
            target,
            _REPOSITORY_EXTENSION,
            relative,
            tomli_w.dumps(dict(initial)).encode("utf-8"),
            boundary=Path(".zpp"),
            create_parents=True,
        )
        values = tomllib.loads(attachment.content.decode("utf-8"))
        return ManagedTraitDocument(
            attachment.path,
            family,
            MappingProxyType(values),
            attachment,
        )


class BundlerLeaseService:
    def __init__(
        self, home: ZppHome, stores: RegisteredStoreProvider | None = None
    ) -> None:
        self._coordinator = LeaseCoordinator(
            stores or OpenSpecStoreProvider(), LeaseStateRepository(home.state_root)
        )

    @staticmethod
    def _member(value: tuple[UUID, str]) -> ChangeMember:
        return ChangeMember(value[0], value[1])

    def acquire(
        self, owner_id: str, members: Iterable[tuple[UUID, str]]
    ) -> AcquisitionResult:
        return self._coordinator.acquire(
            owner_id=owner_id, members=(self._member(value) for value in members)
        )

    def status(self) -> tuple[LeaseBundle, ...]:
        return self._coordinator.repository.read().bundles

    def audit(self, bundle_uuid: UUID, paths: Iterable[Path]) -> AuditResult:
        return self._coordinator.audit(bundle_uuid=bundle_uuid, changed_paths=paths)

    def record_archive(
        self, bundle_uuid: UUID, owner_id: str, member: tuple[UUID, str]
    ) -> LeaseBundle:
        return self._coordinator.record_archive(
            bundle_uuid=bundle_uuid,
            owner_id=owner_id,
            member=self._member(member),
        )

    def complete(self, bundle_uuid: UUID, owner_id: str) -> None:
        self._coordinator.complete(bundle_uuid=bundle_uuid, owner_id=owner_id)

    def abandon(self, bundle_uuid: UUID, owner_id: str) -> None:
        self._coordinator.abandon(bundle_uuid=bundle_uuid, owner_id=owner_id)
