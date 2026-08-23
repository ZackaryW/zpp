from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Protocol
from uuid import UUID, uuid4

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
    RegisteredStore,
)
from openspec_bundler.leases.discovery import RegisteredStoreProvider
from openspec_bundler.leases.manifest import load_manifest

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind
from zpp.utils.processes import ProcessRunner, SubprocessRunner
from zpp.utils.product_home import WorkflowIdentityRepository, ZppHome

_REPOSITORY_EXTENSION = "zpp-traits"
_STORE_EXTENSION = "zpp-traits"
_FAMILY = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


@dataclass(frozen=True, slots=True)
class CoordinationTarget:
    root: Path
    change_name: str

    def __post_init__(self) -> None:
        if not self.change_name.strip():
            raise ValueError("coordination change name must not be empty")


@dataclass(frozen=True, slots=True)
class CoordinationOverrides:
    owner_id: str | None
    stores: tuple[tuple[Path, str], ...]

    def store_id_for(self, root: Path) -> str | None:
        resolved = root.resolve()
        for candidate, store_id in self.stores:
            if candidate == resolved:
                return store_id
        return None


def decode_coordination_overrides(raw: str | None) -> CoordinationOverrides:
    if raw is None:
        return CoordinationOverrides(None, ())
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("invalid ZPP_WORKFLOW_COORDINATION JSON") from error
    if not isinstance(document, dict):
        raise ValueError("ZPP_WORKFLOW_COORDINATION must be an object")
    unknown = sorted(set(document) - {"version", "owner_id", "stores"})
    if unknown:
        raise ValueError(
            "ZPP_WORKFLOW_COORDINATION has unknown field(s): " + ", ".join(unknown)
        )
    version = document.get("version")
    if isinstance(version, bool) or version != 1:
        raise ValueError("ZPP_WORKFLOW_COORDINATION version must be integer 1")
    owner_id = document.get("owner_id")
    if owner_id is not None and (not isinstance(owner_id, str) or not owner_id.strip()):
        raise ValueError("ZPP_WORKFLOW_COORDINATION owner_id must be non-empty")
    raw_stores = document.get("stores", {})
    if not isinstance(raw_stores, dict):
        raise ValueError("ZPP_WORKFLOW_COORDINATION stores must be an object")
    stores: dict[Path, str] = {}
    for raw_root, store_id in raw_stores.items():
        if not isinstance(raw_root, str) or not raw_root.strip():
            raise ValueError("ZPP_WORKFLOW_COORDINATION store roots must be non-empty")
        if not isinstance(store_id, str) or not store_id.strip():
            raise ValueError("ZPP_WORKFLOW_COORDINATION store IDs must be non-empty")
        root = Path(raw_root).resolve()
        if root in stores:
            raise ValueError("ZPP_WORKFLOW_COORDINATION has duplicate resolved roots")
        stores[root] = store_id
    return CoordinationOverrides(
        owner_id,
        tuple(sorted(stores.items(), key=lambda item: str(item[0]))),
    )


class StoreRegistry(RegisteredStoreProvider, Protocol):
    def ensure_registered(
        self, root: Path, *, store_id: str | None = None
    ) -> RegisteredStore: ...


class OpenSpecStoreRegistry:
    """Resolve or create exact OpenSpec registrations through public JSON."""

    def __init__(
        self,
        provider: RegisteredStoreProvider | None = None,
        runner: ProcessRunner | None = None,
    ) -> None:
        self._provider = provider or OpenSpecStoreProvider()
        self._runner = runner or SubprocessRunner()

    def list_stores(self) -> tuple[RegisteredStore, ...]:
        return self._provider.list_stores()

    def ensure_registered(
        self, root: Path, *, store_id: str | None = None
    ) -> RegisteredStore:
        resolved = root.resolve()
        stores = self.list_stores()
        if store_id is not None:
            selected = tuple(store for store in stores if store.store_id == store_id)
            if len(selected) != 1:
                raise ValueError(f"unknown or ambiguous OpenSpec store: {store_id}")
            if selected[0].root.resolve() != resolved:
                raise ValueError("store override does not match resolved root")
            return selected[0]
        matched = tuple(store for store in stores if store.root.resolve() == resolved)
        if len(matched) > 1:
            raise ValueError(f"multiple OpenSpec stores register root: {resolved}")
        if matched:
            return matched[0]
        result = self._runner.run(
            ("openspec", "store", "register", str(resolved), "--yes", "--json"),
            cwd=resolved,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise ValueError(f"OpenSpec store registration failed: {detail}")
        try:
            document = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise ValueError(
                "OpenSpec store registration returned invalid JSON"
            ) from error
        if not isinstance(document, dict) or not isinstance(
            document.get("store"), dict
        ):
            raise ValueError("OpenSpec store registration returned an invalid envelope")
        raw_store = document["store"]
        registered_id = raw_store.get("id")
        registered_root = raw_store.get("root")
        if not isinstance(registered_id, str) or not registered_id.strip():
            raise ValueError("OpenSpec store registration omitted store.id")
        if not isinstance(registered_root, str) or not registered_root.strip():
            raise ValueError("OpenSpec store registration omitted store.root")
        registered = RegisteredStore(registered_id, Path(registered_root).resolve())
        if registered.root != resolved:
            raise ValueError("OpenSpec store registration returned a different root")
        return registered


@dataclass(frozen=True, slots=True)
class ManifestPreparation:
    path: Path
    store_uuid: UUID
    created: bool


class StoreManifestPreparer:
    def ensure(self, root: Path) -> ManifestPreparation:
        resolved = root.resolve()
        openspec_root = resolved / "openspec"
        if not openspec_root.is_dir():
            raise ValueError(f"OpenSpec root is unavailable: {openspec_root}")
        path = openspec_root / "bundler.toml"
        existing = load_manifest(resolved)
        if existing is not None:
            return ManifestPreparation(path, existing.store_uuid, False)
        identity = uuid4()
        payload = f'version = 1\nuuid = "{identity}"\n'
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
        except FileExistsError:
            winner = load_manifest(resolved)
            if winner is None:
                raise ValueError(
                    f"Bundler manifest creation raced without a file: {path}"
                ) from None
            return ManifestPreparation(path, winner.store_uuid, False)
        created = load_manifest(resolved)
        if created is None:
            raise ValueError(f"Bundler manifest was not created: {path}")
        return ManifestPreparation(path, created.store_uuid, True)


@dataclass(frozen=True, slots=True)
class CoordinatedAcquisition:
    coordination: Literal["leased"]
    owner_id: str
    stores: tuple[RegisteredStore, ...]
    manifests: tuple[ManifestPreparation, ...]
    bundle: LeaseBundle
    created: bool


class WorkflowCoordinationService:
    """Runtime-owned bootstrap and exact Bundler acquisition."""

    def __init__(
        self,
        home: ZppHome,
        *,
        registry: StoreRegistry | None = None,
        manifests: StoreManifestPreparer | None = None,
    ) -> None:
        self._home = home
        self._registry = registry or OpenSpecStoreRegistry()
        self._manifests = manifests or StoreManifestPreparer()

    def acquire(
        self,
        targets: Sequence[CoordinationTarget],
        *,
        override_raw: str | None = None,
        owner_id: str | None = None,
    ) -> CoordinatedAcquisition:
        selected = tuple(targets)
        if not selected:
            raise ValueError("at least one coordination target is required")
        roots = tuple(target.root.resolve() for target in selected)
        overrides = decode_coordination_overrides(override_raw)
        stores = tuple(
            self._registry.ensure_registered(
                root,
                store_id=overrides.store_id_for(root),
            )
            for root in roots
        )
        manifests = tuple(self._manifests.ensure(store.root) for store in stores)
        owner = (
            owner_id
            or overrides.owner_id
            or WorkflowIdentityRepository(self._home).resolve()
        )
        acquisition = BundlerLeaseService(self._home, self._registry).acquire(
            owner,
            tuple(
                (manifest.store_uuid, target.change_name)
                for manifest, target in zip(manifests, selected, strict=True)
            ),
        )
        return CoordinatedAcquisition(
            "leased",
            owner,
            stores,
            manifests,
            acquisition.bundle,
            acquisition.created,
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
