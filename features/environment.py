"""behave environment: every scenario runs against an isolated ZPP_HOME and a
snapshot-restored os.environ, so steps exercise the real CLI in-process
without touching the developer's machine state."""

import os
import shutil
import tempfile
from pathlib import Path


def before_scenario(context, scenario):
    context._env_snapshot = dict(os.environ)
    context.tmp = Path(tempfile.mkdtemp(prefix="zpp-bdd-"))
    context.zpp_home = context.tmp / "zpp-home"
    os.environ["ZPP_HOME"] = str(context.zpp_home)
    # Relocate HOME so a surface resolver's auto-detected base dir
    # (Path.home()/.claude) lands inside the hermetic temp tree - the real
    # resolution path is exercised, no test-only base-dir seam needed.
    os.environ["HOME"] = str(context.tmp)
    os.environ.pop("ZPP_TRAITS", None)
    os.environ.pop("ZPP_SAUCEPAN_URL", None)


def make_claude_plugin(context, plugin: str, traits: dict | None = None,
                       skill: bool = False, manifest: bool = False,
                       base: Path | None = None) -> Path:
    """Build a fake installed Claude plugin under base (default ~/.claude), wired
    through installed_plugins.json exactly as the real surface records it.
    traits: {name: content} written into the plugin's traits/ folder."""
    import json

    base = base or (context.tmp / ".claude")
    root = base / "plugins" / "cache" / "mkt" / plugin / "0.0.1"
    root.mkdir(parents=True, exist_ok=True)
    for name, content in (traits or {}).items():
        (root / "traits").mkdir(exist_ok=True)
        (root / "traits" / f"{name}.md").write_text(content + "\n")
    if skill:
        (root / "skills" / f"{plugin}-skill").mkdir(parents=True, exist_ok=True)
        (root / "skills" / f"{plugin}-skill" / "SKILL.md").write_text("a skill\n")
    if manifest:
        (root / "plugin.json").write_text(json.dumps({"name": plugin}))

    index = base / "plugins" / "installed_plugins.json"
    data = json.loads(index.read_text()) if index.is_file() else {"version": 2, "plugins": {}}
    data["plugins"][f"{plugin}@mkt"] = [{"scope": "user", "installPath": str(root)}]
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(json.dumps(data))
    return root


def after_scenario(context, scenario):
    os.environ.clear()
    os.environ.update(context._env_snapshot)
    shutil.rmtree(context.tmp, ignore_errors=True)


def make_fake_saucepan_release(context) -> str:
    """A tiny executable standing in for the saucepan release binary; steps
    point ZPP_SAUCEPAN_URL at it (file://) so managed fetch is exercised for
    real - download, chmod, invoke - without the network."""
    fake = context.tmp / "fake-saucepan"
    fake.write_text("#!/bin/sh\necho '{\"ok\": true}'\n")
    fake.chmod(0o755)
    return fake.as_uri()
