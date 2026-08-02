from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from zpp.utils.control_documents import validate_trigger_config
from zpp.utils.models import (
    AuthoredLayerPaths,
    ManagedStateError,
    TraitCachePaths,
    TraitIndex,
    TriggerRule,
    ValidationIssue,
    ZppValidationError,
)
from zpp.utils.plugin_discovery import ActivePlugin
from zpp.utils.trait_index_loading import load_trait_index


@dataclass(frozen=True, slots=True)
class PluginTraitSource:
    plugin: ActivePlugin
    triggers: Path
    traits: Path


def inspect_plugin_trait_source(plugin: ActivePlugin) -> PluginTraitSource | None:
    triggers = plugin.root / "trait.json"
    traits = plugin.root / "traits"
    trigger_present = triggers.exists() or triggers.is_symlink()
    traits_present = traits.exists() or traits.is_symlink()
    if not trigger_present and not traits_present:
        return None
    if not triggers.is_file():
        raise ManagedStateError(
            f"plugin trait source {plugin.identity!r} has no regular trait.json: {triggers}"
        )
    if not traits.is_dir():
        raise ManagedStateError(
            f"plugin trait source {plugin.identity!r} has no traits directory: {traits}"
        )
    return PluginTraitSource(plugin, triggers, traits)


def plugin_trait_cache_paths(
    user_root: Path,
    source: PluginTraitSource,
) -> TraitCachePaths:
    identity = "\0".join(
        (
            source.plugin.agent,
            source.plugin.identity,
            source.plugin.version,
            source.plugin.root.as_posix(),
        )
    )
    key = sha256(identity.encode("utf-8")).hexdigest()
    root = user_root / "cached" / "plugins" / source.plugin.agent / key
    return TraitCachePaths(
        root=root,
        index=root / "traits.json",
        watch=root / "traits.watch.json",
    )


def read_plugin_trigger_rules(
    source: PluginTraitSource,
) -> tuple[TriggerRule, ...]:
    try:
        value = json.loads(source.triggers.read_text(encoding="utf-8"))
        return validate_trigger_config(value)
    except ZppValidationError as error:
        raise ManagedStateError(f"{source.triggers}: {error}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManagedStateError(f"{source.triggers}: {error}") from error


def load_plugin_trait_index(
    source: PluginTraitSource,
    *,
    user_root: Path,
) -> TraitIndex:
    authored = AuthoredLayerPaths(
        root=source.plugin.root,
        config=source.plugin.root / "config.json",
        triggers=source.triggers,
        traits=source.traits,
    )
    return load_trait_index(
        authored,
        plugin_trait_cache_paths(user_root, source),
    )


def merge_plugin_trait_indexes(
    sources: Sequence[PluginTraitSource],
    indexes: Sequence[TraitIndex],
) -> TraitIndex:
    if len(sources) != len(indexes):
        raise ValueError("plugin trait sources and indexes must have equal length")

    pairs = sorted(
        zip(sources, indexes, strict=True),
        key=lambda pair: pair[0].plugin.identity,
    )
    records = {}
    origins: dict[str, list[PluginTraitSource]] = {}
    conflicts: set[str] = set()
    for source, index in pairs:
        for name, record in index["traits"].items():
            if name not in records:
                records[name] = record
                origins[name] = [source]
                continue
            origins[name].append(source)
            if records[name]["source_sha256"] != record["source_sha256"]:
                conflicts.add(name)

    if conflicts:
        issues = tuple(
            ValidationIssue(
                location=("traits", name),
                message=(
                    f"conflicting plugin trait {name!r} from "
                    + "; ".join(
                        f"{source.plugin.identity} at {source.plugin.root}"
                        for source in origins[name]
                    )
                ),
            )
            for name in sorted(conflicts)
        )
        raise ZppValidationError(issues)

    return {
        "schema_version": 2,
        "traits": {name: records[name] for name in sorted(records)},
    }
