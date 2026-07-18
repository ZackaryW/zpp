import os

import pytest

from zpp.core import sauce


def _fake_release(tmp_path, monkeypatch) -> None:
    fake = tmp_path / "fake-saucepan"
    fake.write_text("#!/bin/sh\necho ok\n")
    fake.chmod(0o755)
    monkeypatch.setenv("ZPP_SAUCEPAN_URL", fake.as_uri())


def test_managed_fetches_once(zpp_home, tmp_path, monkeypatch):
    _fake_release(tmp_path, monkeypatch)
    path1, fetched1 = sauce.ensure_binary("managed")
    path2, fetched2 = sauce.ensure_binary("managed")
    assert path1 == path2 and fetched1 and not fetched2
    assert os.access(path1, os.X_OK)


def test_system_mode_requires_path(zpp_home, monkeypatch):
    monkeypatch.setenv("PATH", str(zpp_home))  # empty dir - nothing resolvable
    with pytest.raises(sauce.SauceError, match="saucepan"):
        sauce.ensure_binary("system")


def test_system_mode_never_writes_bin(zpp_home, monkeypatch):
    monkeypatch.setenv("PATH", str(zpp_home))
    with pytest.raises(sauce.SauceError):
        sauce.ensure_binary("system")
    assert not (zpp_home / "bin").exists()


def test_install_invokes_binary_with_ref(zpp_home, tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    binary = zpp_home / "bin" / "saucepan"
    binary.parent.mkdir(parents=True)
    binary.write_text(f'#!/bin/sh\necho "$@" > {log}\n')
    binary.chmod(0o755)
    sauce.install(binary, "acme-pack")
    assert "install acme-pack" in log.read_text()
