from __future__ import annotations

import json
import os
from pathlib import Path

from zpp.core.errors import ZppDomainError, validation_diagnostic
from zpp.core.state import read_saved_index, require_initialized_user_state
from zpp.utils.control_documents import validate_layer_config, validate_trigger_config
from zpp.utils.git_layers import discover_local_layers, git_worktree_root
from zpp.utils.layouts import authored_layer_paths, trait_cache_paths
from zpp.utils.models import (
    LayerConfig,
    LayerControls,
    LayerRef,
    ManagedStateError,
    CanonicalDirectory,
    AgentName,
    TraitIndex,
    TriggerRule,
    ValidationIssue,
    ZppValidationError,
)
from zpp.utils.paths import (
    canonicalize_existing_directory,
    closest_saved_binding,
    ordered_saved_bindings,
)
from zpp.utils.plugin_discovery import discover_active_plugins
from zpp.utils.plugin_trait_sources import (
    inspect_plugin_trait_source,
    load_plugin_trait_index,
    merge_plugin_trait_indexes,
    read_plugin_trigger_rules,
)
from zpp.utils.trait_composition import (
    apply_trait_config_overlays,
    order_effective_traits,
    select_effective_documents,
)
from zpp.utils.trait_documents import render_trait_document
from zpp.utils.trait_index_loading import load_trait_index
from zpp.utils.triggers import activated_trait_names, compose_trigger_rules


def resolve_traits(
    home: Path,
    target_path: Path,
    *,
    agent: AgentName | None = None,
) -> str:
    target = canonicalize_existing_directory(target_path)
    user_root = require_initialized_user_state(home)
    layers = _participating_layers(user_root, target)

    controls: list[LayerControls] = []
    configurations: list[LayerConfig] = []
    indexes: list[TraitIndex] = []
    if agent is not None:
        sources = tuple(
            sorted(
                (
                    source
                    for plugin in discover_active_plugins(
                        agent,
                        home=home,
                        target=target.resolved,
                    )
                    if (source := inspect_plugin_trait_source(plugin)) is not None
                ),
                key=lambda source: source.plugin.identity,
            )
        )
        if sources:
            plugin_indexes = tuple(
                load_plugin_trait_index(source, user_root=user_root)
                for source in sources
            )
            controls.append(
                LayerControls(
                    triggers=tuple(
                        rule
                        for source in sources
                        for rule in read_plugin_trigger_rules(source)
                    )
                )
            )
            indexes.append(merge_plugin_trait_indexes(sources, plugin_indexes))

    for layer in layers:
        config, trigger_rules = _read_layer_controls(layer.root)
        controls.append(
            LayerControls(
                triggers=trigger_rules,
                trait_overwrites=config.trait_overwrites,
            )
        )
        configurations.append(config)
        authored = authored_layer_paths(layer.root)
        cache = trait_cache_paths(layer, user_root=user_root)
        indexes.append(load_trait_index(authored, cache))

    available = {name for index in indexes for name in index["traits"]}
    unavailable = sorted(
        {
            name
            for config in configurations
            for name in config.traits_config
            if name not in available
        }
    )
    if unavailable:
        raise ZppValidationError(
            tuple(
                ValidationIssue(
                    location=("traitsConfig", name),
                    message=f"configured trait {name!r} has no authored definition",
                )
                for name in unavailable
            )
        )

    activation_order = activated_trait_names(
        compose_trigger_rules(controls),
        target=target.resolved,
    )
    documents = select_effective_documents(activation_order, indexes)
    documents = apply_trait_config_overlays(documents, configurations)
    documents = order_effective_traits(documents, activation_order)
    return "\n".join(render_trait_document(document) for document in documents)


def _participating_layers(
    user_root: Path,
    target: CanonicalDirectory,
) -> tuple[LayerRef, ...]:
    layers: list[LayerRef] = [
        LayerRef(kind="global", root=user_root / "global"),
    ]

    profile = os.environ.get("ZPP_PROFILE")
    if profile:
        profile_root = user_root / "profiles" / profile
        if not profile_root.is_dir():
            raise ZppDomainError(f"unknown profile named by ZPP_PROFILE: {profile}")
        layers.append(LayerRef(kind="profile", root=profile_root, name=profile))

    bindings = ordered_saved_bindings(read_saved_index(user_root.parent))
    saved = closest_saved_binding(target, bindings)
    if saved is not None:
        saved_root = user_root / "saved" / saved.name
        if not saved_root.is_dir():
            raise ZppDomainError(f"missing saved layer: {saved.name} at {saved_root}")
        layers.append(LayerRef(kind="saved", root=saved_root, name=saved.name))

    worktree_path = git_worktree_root(target.resolved)
    if worktree_path is not None:
        worktree = canonicalize_existing_directory(worktree_path)
        for local_root in discover_local_layers(worktree, target):
            layers.append(LayerRef(kind="local", root=local_root))
    return tuple(layers)


def _read_layer_controls(root: Path) -> tuple[LayerConfig, tuple[TriggerRule, ...]]:
    paths = authored_layer_paths(root)
    if not paths.root.is_dir():
        raise ManagedStateError(f"authored layer is missing: {paths.root}")
    if not paths.config.is_file():
        raise ManagedStateError(f"managed config is missing or not a file: {paths.config}")
    if not paths.traits.is_dir():
        raise ManagedStateError(f"trait source directory is missing: {paths.traits}")
    try:
        config = validate_layer_config(
            json.loads(paths.config.read_text(encoding="utf-8"))
        )
        if paths.triggers.exists():
            if not paths.triggers.is_file():
                raise ManagedStateError(
                    f"managed trigger source is not a file: {paths.triggers}"
                )
            triggers = validate_trigger_config(
                json.loads(paths.triggers.read_text(encoding="utf-8"))
            )
        else:
            triggers = ()
        return config, triggers
    except ZppValidationError as error:
        raise ManagedStateError(f"{root}: {validation_diagnostic(error)}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManagedStateError(f"{root}: {error}") from error
