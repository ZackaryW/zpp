from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import UUID

from openspec_bundler import InMemoryStoreProvider, RegisteredStore

import zpp.utils.bundler as bundler_module
from zpp.core.models import SourceKind
from zpp.utils.bundler import BundlerDocuments, BundlerLeaseService
from zpp.utils.processes import SubprocessRunner
from zpp.utils.product_home import ZppHome

PARENT = UUID("52b7223b-3d15-4e8a-98f7-d8ddc90fbf1c")
CHILD = UUID("8f85ef9f-d18a-4787-903e-1ecb920acb77")
SIBLING = UUID("ab776e3f-0b0d-4329-8f54-78acfc1f833b")


def _git(root: Path) -> None:
    root.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)


def _store(
    root: Path, identity: UUID, *, parent: UUID | None, body: str
) -> RegisteredStore:
    manifest = root / "openspec" / "bundler.toml"
    manifest.parent.mkdir(parents=True)
    lines = ["version = 1", f'uuid = "{identity}"']
    if parent is not None:
        lines.append(f'parent = "{parent}"')
    lines.extend(["[extensions.zpp-traits]", body])
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return RegisteredStore(root.name, root)


def test_home_and_process_boundaries_are_provider_free(tmp_path: Path) -> None:
    home = ZppHome(tmp_path / "home")
    result = SubprocessRunner().run(("git", "--version"), cwd=tmp_path)

    assert home.state_root == tmp_path / "home" / "bundler"
    assert result.returncode == 0
    assert "git version" in result.stdout


def test_repository_documents_use_exact_bundler_attachments(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git(repo)
    trait = repo / ".zpp" / "traits" / "bdd.toml"
    trait.parent.mkdir(parents=True)
    trait.write_text(
        '[meta]\nselection = "first-win"\n[[trait]]\n[trait.content]\nbody = "bdd"\n',
        encoding="utf-8",
    )

    documents = BundlerDocuments(InMemoryStoreProvider(()))
    bound = documents.read_repository(repo)

    assert tuple(item.family for item in bound.source.documents) == ("bdd",)
    assert bound.source.documents[0].values["meta"] == {"selection": "first-win"}
    assert not (tmp_path / "home").exists()


def test_selected_store_chain_excludes_sibling(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git(repo)
    parent = _store(repo / "platform", PARENT, parent=None, body='owner = "parent"')
    child = _store(
        repo / "platform" / "api", CHILD, parent=PARENT, body='owner = "child"'
    )
    sibling = _store(
        repo / "platform" / "worker",
        SIBLING,
        parent=PARENT,
        body='owner = "sibling"',
    )
    documents = BundlerDocuments(InMemoryStoreProvider((parent, child, sibling)))

    sources = documents.read_store_chain(child.root)

    assert tuple(source.kind for source in sources) == (
        SourceKind.STORE,
        SourceKind.STORE,
    )
    assert tuple(source.documents[0].values["owner"] for source in sources) == (
        "parent",
        "child",
    )


def test_lease_service_retains_bundle_until_every_archive(tmp_path: Path) -> None:
    parent = _store(tmp_path / "platform", PARENT, parent=None, body='owner = "parent"')
    child = _store(
        tmp_path / "platform" / "api", CHILD, parent=PARENT, body='owner = "child"'
    )
    service = BundlerLeaseService(
        ZppHome(tmp_path / "home"), InMemoryStoreProvider((parent, child))
    )

    result = service.acquire("workflow-1", ((PARENT, "platform:add-auth"),))
    assert result.bundle.held_stores == (PARENT, CHILD)
    retained = service.record_archive(
        result.bundle.bundle_uuid, "workflow-1", (PARENT, "platform:add-auth")
    )
    assert retained.archived_members == retained.members
    service.complete(result.bundle.bundle_uuid, "workflow-1")
    assert service.status() == ()


def test_changed_paths_use_the_most_specific_registered_root(tmp_path: Path) -> None:
    parent = _store(tmp_path / "repo", PARENT, parent=None, body='owner = "parent"')
    child = _store(
        tmp_path / "repo" / "packages" / "app",
        CHILD,
        parent=PARENT,
        body='owner = "child"',
    )
    child_spec = child.root / "openspec" / "specs" / "app" / "spec.md"
    child_product = child.root / "features" / "app.feature"
    parent_spec = parent.root / "openspec" / "proposal.md"
    unknown = tmp_path / "elsewhere" / "proposal.md"

    classified = bundler_module.classify_changed_paths(
        (parent, child),
        (child_spec, child_product, parent_spec, unknown),
    )

    assert classified.openspec == (child_spec.resolve(), parent_spec.resolve())
    assert classified.ignored == (child_product.resolve(),)
    assert classified.violations == (unknown.resolve(),)


def test_lease_audit_partitions_held_unheld_and_unknown_paths(
    tmp_path: Path,
) -> None:
    parent = _store(tmp_path / "repo", PARENT, parent=None, body='owner = "parent"')
    child = _store(
        tmp_path / "repo" / "api", CHILD, parent=PARENT, body='owner = "child"'
    )
    sibling = _store(
        tmp_path / "repo" / "web",
        SIBLING,
        parent=PARENT,
        body='owner = "sibling"',
    )
    service = BundlerLeaseService(
        ZppHome(tmp_path / "home"),
        InMemoryStoreProvider((parent, child, sibling)),
    )
    bundle = service.acquire("workflow-1", ((CHILD, "api-change"),)).bundle
    held_spec = child.root / "openspec" / "specs" / "api" / "spec.md"
    held_product = child.root / "tests" / "test_api.py"
    unheld_spec = sibling.root / "openspec" / "specs" / "web" / "spec.md"
    unknown = tmp_path / "outside" / "test_api.py"

    audit = service.audit(
        bundle.bundle_uuid,
        (held_spec, held_product, unheld_spec, unknown),
    )

    assert audit.accepted == (held_spec.resolve(),)
    assert audit.ignored == (held_product.resolve(),)
    assert audit.violations == (unheld_spec.resolve(), unknown.resolve())
    assert audit.ok is False
