from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from agent_router import Agent
from openspec_bundler import InMemoryStoreProvider, RegisteredStore
from typer.testing import CliRunner

from zpp.artifacts import packaged_companion_skills, packaged_workflow_hook
from zpp.cli import app
from zpp.utils.bundler import (
    BundlerDocuments,
    BundlerLeaseService,
    WorkflowCoordinationService,
)

PARENT = UUID("52b7223b-3d15-4e8a-98f7-d8ddc90fbf1c")
CHILD = UUID("8f85ef9f-d18a-4787-903e-1ecb920acb77")
SIBLING = UUID("ab776e3f-0b0d-4329-8f54-78acfc1f833b")


def _extension(body: str) -> str:
    return f"""
[extensions.zpp-traits.traits.bundle-policy.meta]
selection = "all"

[[extensions.zpp-traits.traits.bundle-policy.trait]]
[extensions.zpp-traits.traits.bundle-policy.trait.content]
body = "{body}"
"""


class Environment:
    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.repository = self.base / "repository"
        self.repository.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repository)], check=True)
        self.home = self.base / "home"
        self.parent = self.repository / "platform"
        self.child = self.parent / "api"
        self.sibling = self.parent / "web"
        stores = (
            self._store(self.parent, PARENT, None, "parent"),
            self._store(self.child, CHILD, PARENT, "child"),
            self._store(self.sibling, SIBLING, PARENT, "sibling"),
        )
        self.provider = InMemoryStoreProvider(stores)
        self.registry = _Registry(self)
        self.unprepared = self.repository / "unprepared"
        self.runner = CliRunner()
        self._patches: list[tuple[object, str, object]] = []
        self._patch_public_adapters()

    def close(self) -> None:
        for module, name, value in reversed(self._patches):
            setattr(module, name, value)
        self._temporary.cleanup()

    def _patch(self, module, name: str, value: object) -> None:
        self._patches.append((module, name, getattr(module, name)))
        setattr(module, name, value)

    def _patch_public_adapters(self) -> None:
        resolution = importlib.import_module("zpp.cli.resolution")
        lease = importlib.import_module("zpp.cli.lease")
        self._patch(
            resolution,
            "BundlerDocuments",
            lambda: BundlerDocuments(self.provider),
        )
        self._patch(
            lease,
            "_service",
            lambda ctx: BundlerLeaseService(ctx.obj.home, self.provider),
        )
        self._patch(
            lease,
            "_coordination_service",
            lambda ctx: WorkflowCoordinationService(
                ctx.obj.home,
                registry=self.registry,
            ),
        )

    @staticmethod
    def _store(
        root: Path, identity: UUID, parent: UUID | None, body: str
    ) -> RegisteredStore:
        manifest = root / "openspec" / "bundler.toml"
        manifest.parent.mkdir(parents=True)
        values = ["version = 1", f'uuid = "{identity}"']
        if parent is not None:
            values.append(f'parent = "{parent}"')
        manifest.write_text("\n".join(values) + _extension(body), encoding="utf-8")
        return RegisteredStore(root.name, root)

    def add_repository_trait(self) -> None:
        path = self.repository / ".zpp" / "traits" / "bundle-policy.toml"
        path.parent.mkdir(parents=True)
        path.write_text(
            '[meta]\nselection = "all"\n\n[[trait]]\n'
            '[trait.content]\nbody = "repository"\n',
            encoding="utf-8",
        )

    def invoke(self, *arguments: str):
        return self.runner.invoke(
            app, ["--path", str(self.home), *arguments], catch_exceptions=False
        )

    def invoke_json(self, *arguments: str) -> dict:
        result = self.invoke(*arguments)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def acquire(self, *members: tuple[UUID, str]) -> dict:
        arguments = ["lease", "acquire", "--owner", "workflow:test"]
        for store, change in members:
            arguments.extend(("--member", f"{store}:{change}"))
        return self.invoke_json(*arguments)

    def use_unprepared_store(self) -> None:
        self.unprepared.mkdir()
        (self.unprepared / "openspec").mkdir()
        self.provider = InMemoryStoreProvider(
            (RegisteredStore("unprepared", self.unprepared),)
        )

    def acquire_target(
        self,
        root: Path,
        change: str,
        *,
        environment: dict[str, str] | None = None,
    ) -> dict:
        result = self.runner.invoke(
            app,
            [
                "--path",
                str(self.home),
                "lease",
                "acquire",
                "--root",
                str(root),
                "--change",
                change,
            ],
            env=environment,
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def status(self) -> dict:
        return self.invoke_json("lease", "status")

    def audit(self, bundle: str, *paths: Path) -> tuple[int, dict]:
        arguments = ["lease", "audit", "--bundle", bundle]
        for path in paths:
            arguments.extend(("--path", str(path)))
        result = self.invoke(*arguments)
        return result.exit_code, json.loads(result.stdout)

    def archive(self, bundle: str, member: tuple[UUID, str]) -> dict:
        return self.invoke_json(
            "lease",
            "archive",
            "--bundle",
            bundle,
            "--owner",
            "workflow:test",
            "--member",
            f"{member[0]}:{member[1]}",
        )

    def complete(self, bundle: str) -> dict:
        return self.invoke_json(
            "lease", "complete", "--bundle", bundle, "--owner", "workflow:test"
        )

    def public_inventory(self) -> dict[str, object]:
        root = self.invoke("--help")
        assert root.exit_code == 0, root.output
        return {
            "help": root.stdout,
            "hook": packaged_workflow_hook(Agent.CODEX).name,
            "skills": tuple(skill.name for skill in packaged_companion_skills()),
        }


class _Registry:
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

    def list_stores(self):
        return self._environment.provider.list_stores()

    def ensure_registered(self, root: Path, *, store_id: str | None = None):
        resolved = root.resolve()
        matches = tuple(
            store
            for store in self.list_stores()
            if store.root.resolve() == resolved
            and (store_id is None or store.store_id == store_id)
        )
        if len(matches) != 1:
            raise ValueError("test registry target is unavailable or ambiguous")
        return matches[0]
