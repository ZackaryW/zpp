from __future__ import annotations

from pathlib import Path

import pytest

from zpp.utils.behavior_mapping import (
    ArgvProvider,
    BehaviorCommand,
    BehaviorMapping,
    BehaviorTarget,
    NxProvider,
    dump_behavior_scaffold,
    load_behavior_mapping,
)
from zpp.utils.models import ManagedStateError


def test_load_behavior_mapping_preserves_declared_order(tmp_path: Path) -> None:
    source = tmp_path / "zpp.behave.yaml"
    source.write_text(
        """version: 1
commands:
  bdd:
    provider:
      kind: argv
      argv: [uv, run, behave, "{targets}"]
    targets:
      workflow:
        value: features/workflow
        paths: [features/workflow/**, src/zpp/utils/skill_*.py]
      core:
        value: features/core
        paths: [features/core/**, src/zpp/core/**]
""",
        encoding="utf-8",
    )

    mapping = load_behavior_mapping(source)

    assert tuple(mapping.commands) == ("bdd",)
    assert tuple(mapping.commands["bdd"].targets) == ("workflow", "core")
    assert isinstance(mapping.commands["bdd"].provider, ArgvProvider)


@pytest.mark.parametrize(
    "yaml_text",
    [
        "version: 1\nversion: 1\ncommands: {}\n",
        "version: 1\ncommands:\n  bdd: {provider: {kind: argv, argv: [x, '{targets}']}, targets: {}}\n  bdd: {}\n",
        "version: 2\ncommands: {}\n",
        "version: 1\nunknown: true\ncommands: {}\n",
        "version: 1\ncommands: {bdd: {provider: {kind: argv, argv: [x]}, targets: {a: {value: a, paths: ['src/**']}}}}\n",
        "version: 1\ncommands: {bdd: {provider: {kind: argv, argv: [x, '{targets}', '{targets}']}, targets: {a: {value: a, paths: ['src/**']}}}}\n",
        "version: 1\ncommands: {bdd: {provider: {kind: argv, argv: [x, '{targets}']}, targets: {a: {value: same, paths: ['src/**']}, b: {value: same, paths: ['tests/**']}}}}\n",
        "version: 1\ncommands: {bdd: {provider: {kind: nx, target: test}, targets: {a: {value: app, paths: ['../outside/**']}}}}\n",
        "version: 1\ncommands: {bdd: {provider: {kind: nx, target: test}, targets: {a: {value: app, paths: ['src/[bad']}}}}\n",
    ],
)
def test_load_behavior_mapping_rejects_ambiguous_or_invalid_yaml(
    tmp_path: Path, yaml_text: str
) -> None:
    source = tmp_path / "zpp.behave.yaml"
    source.write_text(yaml_text, encoding="utf-8")

    with pytest.raises(ManagedStateError, match="behavior mapping"):
        load_behavior_mapping(source)


def test_models_reject_unknown_fields_and_invalid_provider_union() -> None:
    with pytest.raises(ValueError):
        BehaviorMapping.model_validate({"version": 1, "commands": {}, "extra": 1})
    with pytest.raises(ValueError):
        BehaviorCommand.model_validate(
            {
                "provider": {"kind": "other"},
                "targets": {"one": {"value": "one", "paths": ["src/**"]}},
            }
        )


def test_scaffold_is_valid_idempotent_and_preserves_existing_bytes(tmp_path: Path) -> None:
    source = tmp_path / "zpp.behave.yaml"

    assert dump_behavior_scaffold(source) is True
    first = source.read_bytes()
    assert load_behavior_mapping(source) == BehaviorMapping(version=1, commands={})
    assert dump_behavior_scaffold(source) is False
    assert source.read_bytes() == first


def test_typed_models_accept_both_provider_kinds() -> None:
    target = BehaviorTarget(value="app", paths=("src/**",))
    argv = BehaviorCommand(
        provider=ArgvProvider(argv=("uv", "run", "pytest", "{targets}")),
        targets={"app": target},
    )
    nx = BehaviorCommand(
        provider=NxProvider(target="test", args=("--skip-nx-cache",)),
        targets={"app": target},
    )

    assert argv.provider.kind == "argv"
    assert nx.provider.kind == "nx"
