import os
from pathlib import Path

import pytest
from openlease.utils.processes import ProcessResult

from zpp.core.behavior import BehaviorAdapterRegistry, BehaviorProviderError
from zpp.utils.behavior_providers import ArgvAdapter, GoTaskAdapter, NxAdapter


class FakeRunner:
    def __init__(self, results: tuple[ProcessResult, ...] = ()) -> None:
        self.results = list(results)
        self.calls: list[tuple[tuple[str, ...], Path | None]] = []

    def run(self, arguments, *, cwd=None, env=None):
        del env
        self.calls.append((tuple(arguments), cwd))
        if self.results:
            return self.results.pop(0)
        return ProcessResult(tuple(arguments), 0, "", "")


def test_registry_rejects_duplicate_and_unknown_kinds() -> None:
    with pytest.raises(BehaviorProviderError, match="duplicate"):
        BehaviorAdapterRegistry((ArgvAdapter(), ArgvAdapter()))

    registry = BehaviorAdapterRegistry((ArgvAdapter(),))
    with pytest.raises(BehaviorProviderError, match="unknown"):
        registry.validate({"kind": "missing"})


def test_argv_adapter_expands_each_target_as_literal_argv() -> None:
    selected = BehaviorAdapterRegistry((ArgvAdapter(),)).validate(
        {"kind": "argv", "argv": ["runner", "--before", "{targets}", "--after"]}
    )

    arguments = selected.adapter.argv(
        Path.cwd(), selected.settings, ("first target", "$(unsafe);literal")
    )

    assert arguments == (
        "runner",
        "--before",
        "first target",
        "$(unsafe);literal",
        "--after",
    )


@pytest.mark.parametrize(
    "raw",
    [
        {"kind": "argv", "argv": ["runner"]},
        {"kind": "argv", "argv": ["{targets}", "runner"]},
        {"kind": "argv", "argv": ["runner", "{targets}", "{targets}"]},
        {"kind": "argv", "argv": ["runner", "", "{targets}"]},
        {"kind": "argv", "argv": ["runner", "{targets}"], "extra": True},
    ],
)
def test_argv_adapter_rejects_invalid_closed_settings(raw: dict[str, object]) -> None:
    with pytest.raises(BehaviorProviderError):
        ArgvAdapter().validate(raw)


def test_nx_adapter_discovers_and_validates_repository_surface(tmp_path: Path) -> None:
    executable = (
        tmp_path / "node_modules" / ".bin" / ("nx.cmd" if os.name == "nt" else "nx")
    )
    executable.parent.mkdir(parents=True)
    executable.write_text("nx")
    runner = FakeRunner(
        (
            ProcessResult((), 0, '["core"]', ""),
            ProcessResult((), 0, '{"targets":{"bdd":{}}}', ""),
        )
    )
    adapter = NxAdapter(runner=runner)
    settings = adapter.validate(
        {"kind": "nx", "target": "bdd", "args": ["--outputStyle=stream"]}
    )

    arguments = adapter.argv(tmp_path, settings, ("core",))

    assert arguments == (
        str(executable.resolve()),
        "run-many",
        "--target",
        "bdd",
        "--projects",
        "core",
        "--outputStyle=stream",
    )


def test_go_task_adapter_uses_configured_wrapper_and_declared_tasks(
    tmp_path: Path,
) -> None:
    wrapper = tmp_path / "tools" / "task"
    wrapper.parent.mkdir()
    wrapper.write_text("task")
    runner = FakeRunner((ProcessResult((), 0, '{"tasks":[{"name":"test:unit"}]}', ""),))
    adapter = GoTaskAdapter(runner=runner)
    settings = adapter.validate(
        {"kind": "go-task", "executable": "tools/task", "args": ["--silent"]}
    )

    arguments = adapter.argv(tmp_path, settings, ("test:unit",))

    assert arguments == (str(wrapper.resolve()), "--silent", "test:unit")
