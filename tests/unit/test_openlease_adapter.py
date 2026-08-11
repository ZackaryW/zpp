from pathlib import Path

import pytest
from openlease import ConfigurationLayout, InvalidRequest

import zpp.utils.openlease
from zpp.core.models import SourceKind
from zpp.utils.openlease import OpenLeaseTraitDocuments, create_trait_documents


class _Config:
    disposition = object()

    def snapshot(self):
        return {"meta": {"selection": "first-win"}, "trait": []}

    def snapshot_record(self):
        return "provenance"

    def set(self, key, value):
        self.set_call = (key, value)
        return self.disposition


class _Bound:
    config = _Config()


class _Lifecycle:
    def __init__(self) -> None:
        self.bindings = []
        self.initializations = []

    def bind_extension_document(self, binding):
        self.bindings.append(binding)
        return _Bound()

    def initialize_extension_document(
        self, binding, *, initial, boundary=None, create_parents=False
    ):
        self.initializations.append((binding, initial, boundary, create_parents))
        return _Bound()


def test_read_traits_uses_exact_read_only_openlease_binding(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    (traits / "bdd.toml").write_text("[meta]\nselection='first-win'\n")
    lifecycle = _Lifecycle()

    documents = OpenLeaseTraitDocuments(lifecycle).read_traits(repository)

    assert len(documents) == 1
    assert documents[0].family == "bdd"
    binding = lifecycle.bindings[0]
    assert binding.extension_id == "zpp.traits"
    assert binding.codec == "toml"
    assert binding.layout is ConfigurationLayout.DEDICATED
    assert binding.writable is False
    assert binding.repository_path == repository


def test_read_context_returns_none_without_opening_a_missing_document(
    tmp_path: Path,
) -> None:
    lifecycle = _Lifecycle()

    document = OpenLeaseTraitDocuments(lifecycle).read_context(tmp_path)

    assert document is None
    assert lifecycle.bindings == []


def test_initialize_trait_returns_managed_document_not_synthetic_disposition(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    lifecycle = _Lifecycle()
    initial = {"meta": {"selection": "first-win"}, "trait": []}

    document = OpenLeaseTraitDocuments(lifecycle).initialize_trait(
        repository, "bdd", initial
    )

    binding, recorded, boundary, create_parents = lifecycle.initializations[0]
    assert document.family == "bdd"
    assert document.provenance == "provenance"
    assert binding.writable is True
    assert recorded is initial
    assert boundary == repository / ".zpp"
    assert create_parents is True


def test_set_trait_value_returns_real_openlease_disposition(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    (traits / "bdd.toml").write_text("[meta]\nselection='first-win'\n")
    lifecycle = _Lifecycle()

    disposition = OpenLeaseTraitDocuments(lifecycle).set_trait_value(
        repository, "bdd", "meta", {"selection": "extend"}
    )

    assert disposition is _Config.disposition
    assert lifecycle.bindings[0].writable is True
    assert _Bound.config.set_call == ("meta", {"selection": "extend"})


def test_openlease_public_failure_propagates_without_fallback(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    (traits / "bdd.toml").write_text("invalid")

    class RejectingLifecycle(_Lifecycle):
        def bind_extension_document(self, binding):
            raise InvalidRequest("configuration_decode_failed")

    with pytest.raises(InvalidRequest, match="configuration_decode_failed"):
        OpenLeaseTraitDocuments(RejectingLifecycle()).read_traits(repository)


def test_read_repository_adapts_exact_documents_for_core(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    (repository / ".zpp" / "zpp.toml").write_text("[facet]\n")
    (traits / "bdd.toml").write_text("[meta]\nselection='first-win'\n")

    bound = OpenLeaseTraitDocuments(_Lifecycle()).read_repository(repository)

    assert bound.context is not None
    assert bound.context.identifier.endswith("/.zpp/zpp.toml")
    assert bound.source.kind is SourceKind.REPOSITORY
    assert bound.source.identifier == str(repository.resolve())
    assert [item.family for item in bound.source.documents] == ["bdd"]


def test_initialize_context_targets_only_repository_context(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    lifecycle = _Lifecycle()

    document = OpenLeaseTraitDocuments(lifecycle).initialize_context(repository)

    binding, initial, boundary, create_parents = lifecycle.initializations[0]
    assert document.family is None
    assert binding.path == repository.resolve() / ".zpp" / "zpp.toml"
    assert initial == {"facet": {}}
    assert boundary == repository.resolve() / ".zpp"
    assert create_parents is True


def test_create_trait_documents_registers_only_zpp_traits(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured = {}

    class Lifecycle:
        def __init__(self, state_root, *, extensions):
            captured["state_root"] = state_root
            captured["extensions"] = extensions

    monkeypatch.setattr(zpp.utils.openlease, "OpenLease", Lifecycle)

    adapter = create_trait_documents(tmp_path / "state")

    assert isinstance(adapter, OpenLeaseTraitDocuments)
    assert captured["state_root"] == tmp_path / "state"
    registrations = captured["extensions"]
    assert [item.manifest.identifier for item in registrations] == ["zpp.traits"]
