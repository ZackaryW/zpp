from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest
from openspec_bundler import RegisteredStore
from openspec_bundler.leases import LeaseError, ManifestError

from zpp.utils.bundler import (
    CoordinationTarget,
    OpenSpecStoreRegistry,
    StoreManifestPreparer,
    WorkflowCoordinationService,
    decode_coordination_overrides,
)
from zpp.utils.processes import ProcessResult
from zpp.utils.product_home import WorkflowIdentityRepository, ZppHome


class MutableRegistry:
    def __init__(self, stores: tuple[RegisteredStore, ...] = ()) -> None:
        self.stores = stores
        self.registered: list[Path] = []

    def list_stores(self) -> tuple[RegisteredStore, ...]:
        return self.stores

    def ensure_registered(
        self, root: Path, *, store_id: str | None = None
    ) -> RegisteredStore:
        resolved = root.resolve()
        for store in self.stores:
            if store.root.resolve() == resolved:
                if store_id is not None and store.store_id != store_id:
                    raise ValueError("store override does not match resolved root")
                return store
        selected = RegisteredStore(store_id or root.name, resolved)
        self.stores = (*self.stores, selected)
        self.registered.append(resolved)
        return selected


class RecordingRunner:
    def __init__(self, result: ProcessResult) -> None:
        self.result = result
        self.calls: list[tuple[tuple[str, ...], Path]] = []

    def run(self, argv, *, cwd: Path) -> ProcessResult:
        self.calls.append((tuple(argv), cwd))
        return self.result


def test_product_home_identity_is_created_once_and_reused(tmp_path: Path) -> None:
    repository = WorkflowIdentityRepository(ZppHome(tmp_path / "home"))

    first = repository.resolve()
    second = repository.resolve()

    assert first == second
    assert first.startswith("zpp:")
    UUID(first.removeprefix("zpp:"), version=4)
    assert json.loads((tmp_path / "home" / "identity.json").read_text()) == {
        "owner_id": first,
        "version": 1,
    }


def test_product_home_identity_rejects_unknown_fields(tmp_path: Path) -> None:
    identity = tmp_path / "home" / "identity.json"
    identity.parent.mkdir()
    identity.write_text(
        json.dumps({"version": 1, "owner_id": "zpp:test", "extra": True}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"identity.*fields"):
        WorkflowIdentityRepository(ZppHome(identity.parent)).resolve()


def test_coordination_override_is_typed_and_selection_only(tmp_path: Path) -> None:
    root = (tmp_path / "repo").resolve()
    raw = json.dumps(
        {
            "version": 1,
            "owner_id": "workflow:operator",
            "stores": {str(root): "registered-store"},
        }
    )

    overrides = decode_coordination_overrides(raw)

    assert overrides.owner_id == "workflow:operator"
    assert overrides.store_id_for(root) == "registered-store"
    assert not hasattr(overrides, "bypass")


@pytest.mark.parametrize(
    "raw, message",
    [
        ("not-json", "invalid ZPP_WORKFLOW_COORDINATION"),
        ('{"version":1,"bypass":true}', "unknown field"),
        ('{"version":2}', "version"),
        ('{"version":1,"owner_id":""}', "owner_id"),
    ],
)
def test_coordination_override_rejects_unsafe_documents(raw: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        decode_coordination_overrides(raw)


def test_invalid_override_precedes_any_bootstrap_mutation(tmp_path: Path) -> None:
    root = tmp_path / "store"
    (root / "openspec").mkdir(parents=True)
    registry = MutableRegistry()
    service = WorkflowCoordinationService(ZppHome(tmp_path / "home"), registry=registry)

    with pytest.raises(ValueError, match="unknown field"):
        service.acquire(
            (CoordinationTarget(root, "blocked-change"),),
            override_raw='{"version":1,"bypass":true}',
        )

    assert registry.registered == []
    assert not (root / "openspec" / "bundler.toml").exists()
    assert not (tmp_path / "home").exists()


def test_store_manifest_preparation_is_idempotent(tmp_path: Path) -> None:
    root = tmp_path / "store"
    (root / "openspec").mkdir(parents=True)
    preparer = StoreManifestPreparer()

    first = preparer.ensure(root)
    second = preparer.ensure(root)

    assert first.store_uuid == second.store_uuid
    assert first.created is True
    assert second.created is False
    assert first.path == root / "openspec" / "bundler.toml"


def test_store_manifest_preparation_never_repairs_invalid_state(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "store" / "openspec" / "bundler.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('version = 1\nuuid = "invalid"\n', encoding="utf-8")

    with pytest.raises(ManifestError, match="invalid UUID"):
        StoreManifestPreparer().ensure(tmp_path / "store")

    assert 'uuid = "invalid"' in manifest.read_text(encoding="utf-8")


def test_registry_automatically_registers_an_unmatched_root(tmp_path: Path) -> None:
    root = (tmp_path / "repository").resolve()
    root.mkdir()
    payload = json.dumps(
        {
            "store": {"id": "repository", "root": str(root)},
            "registry": {
                "path": str(tmp_path / "registry.yaml"),
                "registered": True,
                "already_registered": False,
            },
            "git": {
                "is_repository": True,
                "initialized": False,
                "committed": False,
            },
            "created_files": [".openspec-store/store.yaml"],
            "status": [],
        }
    )
    runner = RecordingRunner(
        ProcessResult(
            ("openspec", "store", "register"),
            0,
            payload,
            "",
        )
    )
    registry = OpenSpecStoreRegistry(provider=MutableRegistry(), runner=runner)

    registered = registry.ensure_registered(root)

    assert registered == RegisteredStore("repository", root)
    assert runner.calls == [
        (("openspec", "store", "register", str(root), "--yes", "--json"), root)
    ]


def test_runtime_owns_preparation_identity_and_exact_acquisition(
    tmp_path: Path,
) -> None:
    root = tmp_path / "store"
    (root / "openspec").mkdir(parents=True)
    registry = MutableRegistry((RegisteredStore("store", root),))
    service = WorkflowCoordinationService(ZppHome(tmp_path / "home"), registry=registry)

    result = service.acquire((CoordinationTarget(root, "add-runtime-flow"),))

    assert result.coordination == "leased"
    assert result.owner_id.startswith("zpp:")
    assert result.bundle.owner_id == result.owner_id
    assert result.bundle.members[0].change_name == "add-runtime-flow"
    assert result.manifests[0].created is True
    assert registry.registered == []


def test_runtime_owner_override_still_acquires_a_bundle(tmp_path: Path) -> None:
    root = tmp_path / "store"
    (root / "openspec").mkdir(parents=True)
    registry = MutableRegistry((RegisteredStore("store", root),))
    service = WorkflowCoordinationService(ZppHome(tmp_path / "home"), registry=registry)

    result = service.acquire(
        (CoordinationTarget(root, "override-owner"),),
        override_raw='{"version":1,"owner_id":"workflow:override"}',
    )

    assert result.owner_id == "workflow:override"
    assert result.bundle.owner_id == "workflow:override"
    assert result.coordination == "leased"


def test_runtime_preserves_a_real_bundle_conflict(tmp_path: Path) -> None:
    root = tmp_path / "store"
    (root / "openspec").mkdir(parents=True)
    registry = MutableRegistry((RegisteredStore("store", root),))
    service = WorkflowCoordinationService(ZppHome(tmp_path / "home"), registry=registry)
    service.acquire(
        (CoordinationTarget(root, "held-change"),),
        owner_id="workflow:first",
    )

    with pytest.raises(LeaseError):
        service.acquire(
            (CoordinationTarget(root, "other-change"),),
            owner_id="workflow:second",
        )
