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


# --- release asset naming: must match saucepan's real Rust-target-triple
# assets (verified against github.com/ZackaryW/saucepan/releases). The
# fake-URL tests above never exercise this, which is how the 404 slipped. ---

def test_asset_name_macos_is_universal():
    # one asset covers both arches; no arch-token mapping to get wrong
    assert sauce._asset_name("darwin", "arm64") == "saucepan-universal-apple-darwin"
    assert sauce._asset_name("darwin", "x86_64") == "saucepan-universal-apple-darwin"


def test_asset_name_windows_triple_with_exe():
    assert sauce._asset_name("windows", "amd64") == "saucepan-x86_64-pc-windows-msvc.exe"
    assert sauce._asset_name("windows", "x86_64") == "saucepan-x86_64-pc-windows-msvc.exe"
    assert sauce._asset_name("windows", "arm64") == "saucepan-aarch64-pc-windows-msvc.exe"


def test_asset_name_linux_has_no_published_binary():
    # upstream ships no linux asset; managed mode must say so, not 404
    with pytest.raises(sauce.SauceError, match="linux"):
        sauce._asset_name("linux", "x86_64")


def test_release_url_uses_real_asset_name(monkeypatch):
    monkeypatch.delenv("ZPP_SAUCEPAN_URL", raising=False)
    monkeypatch.setattr(sauce.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(sauce.platform, "machine", lambda: "arm64")
    url = sauce._release_url()
    assert url.endswith("/releases/latest/download/saucepan-universal-apple-darwin")


def test_release_url_env_override_wins(monkeypatch):
    monkeypatch.setenv("ZPP_SAUCEPAN_URL", "file:///tmp/pinned")
    assert sauce._release_url() == "file:///tmp/pinned"


def test_install_invokes_binary_with_ref(zpp_home, tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    binary = zpp_home / "bin" / "saucepan"
    binary.parent.mkdir(parents=True)
    binary.write_text(f'#!/bin/sh\necho "$@" > {log}\n')
    binary.chmod(0o755)
    sauce.install(binary, "acme-pack")
    assert "install acme-pack" in log.read_text()
