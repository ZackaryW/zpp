"""Packaged ZPP source assets."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import as_file, files
from types import MappingProxyType
from typing import Final

from agent_router import Agent, Hook, Skill

from zpp.core.application import BoundTraitDocument, BoundTraitSource
from zpp.core.models import SourceKind
from zpp.core.workflows import (
    ComponentContract,
    WorkflowContract,
    WorkflowContractError,
    decode_component_contract,
    decode_workflow_contract,
    validate_contract_inventory,
)


@dataclass(frozen=True, slots=True)
class PackagedTrait:
    family: str
    content: bytes


@dataclass(frozen=True, slots=True)
class PackagedJsonSchema:
    name: str
    document: Mapping[str, object]


WORKFLOW_SKILL_ROLE: Final[str] = "workflow"
COMPANION_SKILL_ROLE: Final[str] = "companion"

WORKFLOW_ENTRY_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpp-auto",
    "zpp-new-feature",
    "zpp-fix-bug",
    "zpp-scaffold",
    "zpp-generic-workflow",
    "zpp-legacy-workflow",
)
COMPLETE_WORKFLOW_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpp-new-feature",
    "zpp-fix-bug",
    "zpp-scaffold",
    "zpp-generic-workflow",
)
WORKFLOW_KERNEL_SKILL_NAME: Final[str] = "zpps-workflow-kernel"
WORKFLOW_STAGE_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpps-clarify",
    "zpps-shape-bdd",
    "zpps-planning-ponytail",
    "zpps-mature-utilities",
    "zpps-wire",
    "zpps-form-specs",
    "zpps-finalize",
)
OPENSPEC_ADAPTER_SKILL_NAMES: Final[tuple[str, ...]] = (
    "zpps-explore",
    "zpps-new-change",
    "zpps-continue-change",
    "zpps-ff-change",
    "zpps-propose-change",
    "zpps-update-change",
    "zpps-apply-change",
    "zpps-verify-change",
    "zpps-sync-specs",
    "zpps-archive-change",
    "zpps-bulk-archive-change",
)
REPOSITORY_EVIDENCE_SKILL_NAME: Final[str] = "zpps-verify-repository"
WORKFLOW_SKILL_NAMES: Final[tuple[str, ...]] = (
    *WORKFLOW_ENTRY_SKILL_NAMES,
    WORKFLOW_KERNEL_SKILL_NAME,
    *WORKFLOW_STAGE_SKILL_NAMES,
    *OPENSPEC_ADAPTER_SKILL_NAMES,
    REPOSITORY_EVIDENCE_SKILL_NAME,
)

_SKILL_DOCUMENT = "SKILL.md"
class PackagedSkillError(ValueError):
    pass


def _skill_document(skill: Skill) -> str:
    documents = tuple(
        item for item in skill.files if item.relative_path == _SKILL_DOCUMENT
    )
    if len(documents) != 1:
        raise PackagedSkillError(
            f"packaged workflow member {skill.name!r} must contain one "
            f"{_SKILL_DOCUMENT}"
        )
    return documents[0].content.decode("utf-8")


def _role_skill_names(role: str) -> tuple[str, ...]:
    root = files("zpp.artifacts").joinpath("skills", role)
    if not root.is_dir():
        raise PackagedSkillError(f"packaged skill role is missing: {role}")
    return tuple(
        sorted(
            (
                item.name
                for item in root.iterdir()
                if item.is_dir() and item.joinpath(_SKILL_DOCUMENT).is_file()
            ),
            key=lambda name: (name.casefold(), name),
        )
    )


def _load_role_skills(role: str) -> tuple[Skill, ...]:
    root = files("zpp.artifacts").joinpath("skills", role)
    loaded: list[Skill] = []
    for name in _role_skill_names(role):
        with as_file(root.joinpath(name)) as path:
            loaded.append(Skill.from_path(path))
    return tuple(loaded)


def packaged_workflow_skills() -> tuple[Skill, ...]:
    discovered = _role_skill_names(WORKFLOW_SKILL_ROLE)
    expected = frozenset(WORKFLOW_SKILL_NAMES)
    actual = frozenset(discovered)
    if actual != expected or len(discovered) != len(WORKFLOW_SKILL_NAMES):
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise PackagedSkillError(
            "packaged workflow family does not match its canonical inventory: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    root = files("zpp.artifacts").joinpath("skills", WORKFLOW_SKILL_ROLE)
    loaded: list[Skill] = []
    for name in WORKFLOW_SKILL_NAMES:
        with as_file(root.joinpath(name)) as path:
            skill = Skill.from_path(path)
        if skill.name != name:
            raise PackagedSkillError(
                f"packaged workflow member {name!r} declares name {skill.name!r}"
            )
        loaded.append(skill)
    return tuple(loaded)


def packaged_companion_skills() -> tuple[Skill, ...]:
    loaded = _load_role_skills(COMPANION_SKILL_ROLE)
    if not loaded:
        raise PackagedSkillError("packaged companion role contains no skill")
    return loaded


def packaged_workflow_hook(agent: Agent) -> Hook:
    relative_paths = {
        Agent.CODEX: ("hooks", "codex", "zpp-traits.json"),
        Agent.CLAUDE: ("hooks", "claude", "zpp-traits.json"),
        Agent.KIMI: ("hooks", "kimi", "zpp-traits.toml"),
        Agent.PI: ("hooks", "pi", "zpp-traits.ts"),
    }
    resource = files("zpp.artifacts").joinpath(*relative_paths[agent])
    with as_file(resource) as path:
        return Hook.from_path(path, source_agent=agent)


def packaged_workflow_reminder_hook(agent: Agent) -> Hook | None:
    relative_paths = {
        Agent.CODEX: ("hooks", "codex", "zpp-workflow-reminder.json"),
        Agent.CLAUDE: ("hooks", "claude", "zpp-workflow-reminder.json"),
    }
    relative_path = relative_paths.get(agent)
    if relative_path is None:
        return None
    resource = files("zpp.artifacts").joinpath(*relative_path)
    with as_file(resource) as path:
        return Hook.from_path(path, source_agent=agent)


def packaged_workflow_contracts() -> tuple[WorkflowContract, ...]:
    root = files("zpp.artifacts").joinpath("workflow_contracts", "workflows")
    discovered = _json_resource_names(root)
    expected = tuple(f"{name}.json" for name in COMPLETE_WORKFLOW_SKILL_NAMES)
    _require_resource_names(discovered, expected, "workflow contract")
    workflows = tuple(
        decode_workflow_contract(
            _read_json_object(root.joinpath(name)),
            source=f"workflow_contracts/workflows/{name}",
        )
        for name in expected
    )
    components = packaged_component_contracts()
    skills = packaged_workflow_skills()
    actual_workflows = tuple(
        skill.name for skill in skills if skill.name in COMPLETE_WORKFLOW_SKILL_NAMES
    )
    validate_contract_inventory(
        workflows,
        components,
        workflow_names=actual_workflows,
        component_names=tuple(
            skill.name for skill in skills if skill.name.startswith("zpps-")
        ),
    )
    return workflows


def packaged_component_contracts() -> tuple[ComponentContract, ...]:
    root = files("zpp.artifacts").joinpath("workflow_contracts", "components")
    names = _component_contract_names()
    expected = tuple(f"{name}.json" for name in names)
    discovered = _json_resource_names(root)
    _require_resource_names(discovered, expected, "component contract")
    components = tuple(
        decode_component_contract(
            _read_json_object(root.joinpath(name)),
            source=f"workflow_contracts/components/{name}",
        )
        for name in expected
    )
    actual_components = tuple(
        skill.name
        for skill in packaged_workflow_skills()
        if skill.name.startswith("zpps-")
    )
    validate_contract_inventory(
        (),
        components,
        workflow_names=(),
        component_names=actual_components,
    )
    return components


def packaged_workflow_contract_schemas() -> tuple[PackagedJsonSchema, ...]:
    root = files("zpp.artifacts").joinpath("workflow_contracts", "schemas")
    expected = (
        "component-contract.schema.json",
        "workflow-contract.schema.json",
    )
    discovered = _json_resource_names(root)
    _require_resource_names(discovered, expected, "workflow contract schema")
    return tuple(
        PackagedJsonSchema(
            name,
            MappingProxyType(_read_json_object(root.joinpath(name))),
        )
        for name in expected
    )


def _component_contract_names() -> tuple[str, ...]:
    return tuple(name for name in WORKFLOW_SKILL_NAMES if name.startswith("zpps-"))


def _json_resource_names(root) -> tuple[str, ...]:
    if not root.is_dir():
        raise WorkflowContractError(f"packaged JSON resource root is missing: {root}")
    return tuple(
        sorted(
            (item.name for item in root.iterdir() if item.is_file()),
            key=lambda name: (name.casefold(), name),
        )
    )


def _require_resource_names(
    discovered: tuple[str, ...], expected: tuple[str, ...], kind: str
) -> None:
    if set(discovered) != set(expected) or len(discovered) != len(expected):
        missing = sorted(set(expected) - set(discovered))
        unexpected = sorted(set(discovered) - set(expected))
        raise WorkflowContractError(
            f"packaged {kind} inventory is invalid: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )


def _read_json_object(resource) -> dict[str, object]:
    try:
        value = json.loads(resource.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError, OSError) as error:
        raise WorkflowContractError(f"{resource}: invalid JSON") from error
    if not isinstance(value, dict):
        raise WorkflowContractError(f"{resource}: JSON document must be an object")
    return value


def packaged_traits() -> tuple[PackagedTrait, ...]:
    root = files("zpp.artifacts").joinpath("traits")
    documents = sorted(
        (
            item
            for item in root.iterdir()
            if item.is_file() and item.name.endswith(".toml")
        ),
        key=lambda item: (item.name.casefold(), item.name),
    )
    return tuple(
        PackagedTrait(item.name.removesuffix(".toml"), item.read_bytes())
        for item in documents
    )


def packaged_trait_source() -> BoundTraitSource:
    documents = tuple(
        BoundTraitDocument(
            family=item.family,
            values=tomllib.loads(item.content.decode("utf-8")),
            identifier=f"zpp:packaged:{item.family}",
            order=order,
        )
        for order, item in enumerate(packaged_traits())
    )
    return BoundTraitSource(
        kind=SourceKind.GLOBAL,
        identifier="zpp:packaged",
        order=10_000,
        documents=documents,
    )


__all__ = [
    "COMPANION_SKILL_ROLE",
    "COMPLETE_WORKFLOW_SKILL_NAMES",
    "OPENSPEC_ADAPTER_SKILL_NAMES",
    "REPOSITORY_EVIDENCE_SKILL_NAME",
    "WORKFLOW_ENTRY_SKILL_NAMES",
    "WORKFLOW_KERNEL_SKILL_NAME",
    "WORKFLOW_SKILL_NAMES",
    "WORKFLOW_SKILL_ROLE",
    "WORKFLOW_STAGE_SKILL_NAMES",
    "PackagedJsonSchema",
    "PackagedSkillError",
    "PackagedTrait",
    "packaged_companion_skills",
    "packaged_component_contracts",
    "packaged_trait_source",
    "packaged_traits",
    "packaged_workflow_contract_schemas",
    "packaged_workflow_contracts",
    "packaged_workflow_hook",
    "packaged_workflow_reminder_hook",
    "packaged_workflow_skills",
]
