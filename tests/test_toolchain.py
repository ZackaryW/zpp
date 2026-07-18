from zpp.core import toolchain


def test_doctor_and_bootstrap_consume_the_same_table(monkeypatch):
    monkeypatch.setattr(toolchain.shutil, "which", lambda cmd: None)
    report, _ = toolchain.doctor()
    missing = {r["tool"] for r in report
               if not r["present"] and not r.get("detect_only")}
    installed, manual, _ = toolchain.bootstrap(dry_run=True)
    touched = {i.split(":")[0] for i in installed} | {m.split(":")[0] for m in manual}
    assert missing == touched  # they can never disagree about installable tools


def test_doctor_is_detect_only(monkeypatch):
    monkeypatch.setattr(toolchain.shutil, "which", lambda cmd: "/bin/" + cmd)
    monkeypatch.setattr(
        toolchain.subprocess, "run",
        lambda *a, **k: type("P", (), {"stdout": "v1.0\n", "returncode": 0})(),
    )
    report, _ = toolchain.doctor()
    assert all(r["present"] for r in report)


def test_bootstrap_idempotent_when_complete(monkeypatch):
    monkeypatch.setattr(toolchain.shutil, "which", lambda cmd: "/bin/" + cmd)
    installed, manual, _ = toolchain.bootstrap()
    assert installed == [] and manual == []


def test_partial_installability_reports_manual(monkeypatch):
    monkeypatch.setattr(toolchain.shutil, "which", lambda cmd: None)
    monkeypatch.setattr(toolchain.platform, "system", lambda: "Linux")
    installed, manual, _ = toolchain.bootstrap(dry_run=True)
    assert any(m.startswith("node:") for m in manual)  # no non-interactive path on Linux
    assert any(i.startswith("zmem:") for i in installed)  # uv path exists everywhere
