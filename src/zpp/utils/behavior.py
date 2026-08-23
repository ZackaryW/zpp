from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml
from openspec_bundler import AttachmentService, OpenSpecStoreProvider
from openspec_bundler.leases.discovery import RegisteredStoreProvider

from zpp.core.behavior import (
    BehaviorAdapterRegistry,
    BehaviorExecutionError,
    BehaviorExecutionReport,
    BehaviorInitializationReport,
    BehaviorProviderAdapter,
    BehaviorRunInput,
    parse_behavior_mapping,
    select_behavior_targets,
)
from zpp.utils.behavior_providers import (
    behavior_provider_diagnostics,
    default_behavior_adapters,
)
from zpp.utils.processes import ProcessRunner, SubprocessRunner

_EXTENSION = "zpp-behave"
_DOCUMENT = Path("zpp.behave.yaml")


class GitPaths:
    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self._runner = runner or SubprocessRunner()

    def root(self, target: Path) -> Path:
        result = self._runner.run(
            ("git", "rev-parse", "--show-toplevel"), cwd=target.resolve()
        )
        if result.returncode:
            raise ValueError((result.stderr or result.stdout).strip())
        return Path(result.stdout.strip()).resolve()

    def changed(
        self, root: Path, base: str | None, head: str | None
    ) -> tuple[str, ...]:
        if base is not None:
            result = self._runner.run(
                ("git", "diff", "--name-only", "-z", base, head or ""), cwd=root
            )
            return self._paths(result, "Git revision comparison")
        tracked = self._runner.run(
            ("git", "diff", "--name-only", "-z", "HEAD"), cwd=root
        )
        untracked = self._runner.run(
            ("git", "ls-files", "--others", "--exclude-standard", "-z"), cwd=root
        )
        return tuple(
            dict.fromkeys(
                (
                    *self._paths(tracked, "Git worktree inspection"),
                    *self._paths(untracked, "Git untracked-file inspection"),
                )
            )
        )

    @staticmethod
    def _paths(result, operation: str) -> tuple[str, ...]:
        if result.returncode:
            raise BehaviorExecutionError(
                f"{operation} failed: "
                + (result.stderr or result.stdout or str(result.returncode)).strip()
            )
        return tuple(value for value in result.stdout.split("\0") if value)


class BundlerBehaviorDocuments:
    def __init__(
        self,
        stores: RegisteredStoreProvider | None = None,
        *,
        adapters: Sequence[BehaviorProviderAdapter] | None = None,
        runner: ProcessRunner | None = None,
        git: GitPaths | None = None,
    ) -> None:
        self._attachments = AttachmentService(stores or OpenSpecStoreProvider())
        self._runner = runner or SubprocessRunner()
        self._git = git or GitPaths(self._runner)
        self._adapters = tuple(
            default_behavior_adapters(self._runner) if adapters is None else adapters
        )

    def initialize(self, repository: Path) -> BehaviorInitializationReport:
        target = self._attachments.repository_from_path(repository)
        attachment = self._attachments.read_repository(target, _EXTENSION, _DOCUMENT)
        if attachment is None:
            attachment = self._attachments.initialize_repository(
                target,
                _EXTENSION,
                _DOCUMENT,
                yaml.safe_dump({"version": 1, "commands": {}}, sort_keys=False).encode(
                    "utf-8"
                ),
                boundary=Path("."),
            )
        mapping = self._mapping(attachment.content)
        return BehaviorInitializationReport(
            target.root,
            tuple(mapping.commands),
            behavior_provider_diagnostics(target.root),
        )

    def run(
        self, repository: Path, request: BehaviorRunInput
    ) -> BehaviorExecutionReport:
        target = self._attachments.repository_from_path(repository)
        attachment = self._attachments.read_repository(target, _EXTENSION, _DOCUMENT)
        if attachment is None:
            raise BehaviorExecutionError(
                f"behavior mapping is absent: {target.root / _DOCUMENT}"
            )
        mapping = self._mapping(attachment.content)
        command = mapping.commands.get(request.command)
        if command is None:
            raise BehaviorExecutionError(
                f"behavior command is not declared: {request.command}"
            )
        changed_paths: tuple[str, ...] = ()
        if not (request.complete or request.targets or request.gate is not None):
            changed_paths = self._git.changed(target.root, request.base, request.head)
        targets = select_behavior_targets(command, request, changed_paths=changed_paths)
        if not targets:
            return BehaviorExecutionReport(target.root, request.command, (), None)
        values = tuple(item.value for item in targets)
        argv = command.provider.adapter.argv(
            target.root, command.provider.settings, values
        )
        if not argv or not argv[0]:
            raise BehaviorExecutionError(
                "behavior adapter returned an empty executable"
            )
        return BehaviorExecutionReport(
            target.root,
            request.command,
            targets,
            self._runner.run(argv, cwd=target.root),
        )

    def _mapping(self, content: bytes):
        try:
            raw = yaml.safe_load(content.decode("utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError) as error:
            raise ValueError(f"invalid behavior configuration: {error}") from error
        if not isinstance(raw, Mapping):
            raise ValueError("behavior configuration is not a mapping")
        return parse_behavior_mapping(
            dict(raw), registry=BehaviorAdapterRegistry(self._adapters)
        )
