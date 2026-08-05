from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from zpp.utils.filesystem_mutation import FilesystemMutationPlan
from zpp.utils.models import AgentName, CreationEntry, CreationPlan, ManagedStateError
from zpp.utils.openspec_skills import (
    GeneratedOpenSpecBundle,
    OPENSPEC_CORE_SKILL_NAMES,
)
from zpp.utils.skill_bundles import SkillFile, fingerprint_skill_files


OPENSPEC_SKILL_MANIFEST_NAME = ".zpp-openspec-skills.json"


class OpenSpecSkillManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    agent: AgentName
    openspec_version: str | None
    fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    files: dict[str, str]

    @field_validator("files")
    @classmethod
    def validate_files(cls, value: dict[str, str]) -> dict[str, str]:
        for path, digest in value.items():
            relative = PurePosixPath(path)
            if (
                not path
                or "\\" in path
                or relative.is_absolute()
                or path != relative.as_posix()
                or ".." in relative.parts
                or len(relative.parts) < 2
                or relative.parts[0] not in OPENSPEC_CORE_SKILL_NAMES
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError(f"invalid generated skill path or digest: {path}")
        return value

    @model_validator(mode="after")
    def require_core_documents(self) -> OpenSpecSkillManifest:
        required = {f"{name}/SKILL.md" for name in OPENSPEC_CORE_SKILL_NAMES}
        if not required.issubset(self.files):
            raise ValueError("manifest does not own every OpenSpec core skill document")
        if self.skill_names != OPENSPEC_CORE_SKILL_NAMES:
            raise ValueError("manifest owns an unexpected OpenSpec skill inventory")
        return self

    @property
    def skill_names(self) -> tuple[str, ...]:
        return tuple(sorted({path.split("/", 1)[0] for path in self.files}))


@dataclass(frozen=True, slots=True)
class OpenSpecProjectionInspection:
    root: Path
    state: Literal["absent", "compatible", "outdated", "conflict"]
    manifest: OpenSpecSkillManifest | None = None
    reason: str | None = None


def inspect_openspec_projection(
    root: Path,
    agent: AgentName,
    detected_version: str | None,
) -> OpenSpecProjectionInspection:
    manifest_path = root / OPENSPEC_SKILL_MANIFEST_NAME
    manifest_present = manifest_path.exists() or manifest_path.is_symlink()
    claimed_present = any(
        (root / name).exists() or (root / name).is_symlink()
        for name in OPENSPEC_CORE_SKILL_NAMES
    )
    if not manifest_present:
        if claimed_present:
            return OpenSpecProjectionInspection(
                root, "conflict", reason="unmanaged OpenSpec skill collision"
            )
        return OpenSpecProjectionInspection(root, "absent")

    try:
        manifest = _load_manifest(manifest_path)
        if manifest.agent != agent:
            raise ManagedStateError("generated OpenSpec manifest agent differs")
        actual = _read_projection_files(root, manifest)
    except (ManagedStateError, OSError, UnicodeError, ValueError) as error:
        return OpenSpecProjectionInspection(root, "conflict", reason=str(error))

    if set(actual) != set(manifest.files):
        return OpenSpecProjectionInspection(
            root,
            "conflict",
            manifest,
            "managed OpenSpec file set differs from its manifest",
        )
    if any(
        sha256(file.content).hexdigest() != manifest.files[path]
        for path, file in actual.items()
    ):
        return OpenSpecProjectionInspection(
            root,
            "conflict",
            manifest,
            "managed OpenSpec content differs from its manifest",
        )
    if fingerprint_skill_files(actual.values()) != manifest.fingerprint:
        return OpenSpecProjectionInspection(
            root,
            "conflict",
            manifest,
            "managed OpenSpec fingerprint differs from its manifest",
        )
    state: Literal["compatible", "outdated"] = (
        "compatible"
        if manifest.openspec_version == detected_version
        else "outdated"
    )
    return OpenSpecProjectionInspection(root, state, manifest)


def plan_openspec_projection(
    root: Path,
    bundle: GeneratedOpenSpecBundle,
    inspection: OpenSpecProjectionInspection,
) -> FilesystemMutationPlan:
    if inspection.root != root:
        raise ValueError("OpenSpec inspection root differs from destination")
    if inspection.state == "conflict":
        raise ManagedStateError(f"conflicting OpenSpec skill projection: {root}")
    if inspection.state == "compatible":
        return FilesystemMutationPlan(CreationPlan(()))
    if inspection.manifest is not None and inspection.manifest.agent != bundle.agent:
        raise ManagedStateError("OpenSpec projection agent differs from generated bundle")

    directories = set(_missing_directories(root))
    entries: list[CreationEntry] = []
    for file in bundle.files:
        destination = root.joinpath(*file.relative_path.split("/"))
        cursor = destination.parent
        while cursor != root:
            directories.add(cursor)
            cursor = cursor.parent
        directories.add(root / file.relative_path.split("/", 1)[0])
    entries.extend(
        CreationEntry(path, "directory")
        for path in sorted(directories, key=lambda item: (len(item.parts), str(item)))
    )
    entries.extend(
        CreationEntry(
            root.joinpath(*file.relative_path.split("/")),
            "binary",
            file.content,
        )
        for file in bundle.files
    )
    manifest = OpenSpecSkillManifest(
        agent=bundle.agent,
        openspec_version=bundle.version,
        fingerprint=bundle.fingerprint,
        files={
            file.relative_path: sha256(file.content).hexdigest()
            for file in bundle.files
        },
    )
    entries.append(
        CreationEntry(
            root / OPENSPEC_SKILL_MANIFEST_NAME,
            "text",
            json.dumps(
                manifest.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
    )
    replacements: tuple[Path, ...] = ()
    if inspection.state == "outdated":
        assert inspection.manifest is not None
        replacements = tuple(root / name for name in inspection.manifest.skill_names) + (
            root / OPENSPEC_SKILL_MANIFEST_NAME,
        )
    return FilesystemMutationPlan(CreationPlan(tuple(entries)), replacements)


def _load_manifest(path: Path) -> OpenSpecSkillManifest:
    if path.is_symlink() or not path.is_file():
        raise ManagedStateError(f"OpenSpec skill manifest is not a regular file: {path}")
    try:
        return OpenSpecSkillManifest.model_validate_json(path.read_bytes())
    except (OSError, UnicodeError, ValidationError) as error:
        raise ManagedStateError(f"OpenSpec skill manifest is invalid: {path}") from error


def _read_projection_files(
    root: Path,
    manifest: OpenSpecSkillManifest,
) -> dict[str, SkillFile]:
    if root.is_symlink() or not root.is_dir():
        raise ManagedStateError(f"OpenSpec skill root is not a regular directory: {root}")
    result: dict[str, SkillFile] = {}
    for name in manifest.skill_names:
        skill = root / name
        if skill.is_symlink() or not skill.is_dir():
            raise ManagedStateError(f"managed OpenSpec skill directory is invalid: {skill}")
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise ManagedStateError(f"managed OpenSpec content contains a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(root).as_posix()
                result[relative] = SkillFile(relative, path.read_bytes())
            elif not path.is_dir():
                raise ManagedStateError(f"managed OpenSpec content is invalid: {path}")
    return result


def _missing_directories(root: Path) -> tuple[Path, ...]:
    missing: list[Path] = []
    cursor = root
    while not cursor.exists() and not cursor.is_symlink():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise ManagedStateError(f"OpenSpec skill projection parent is not a directory: {cursor}")
    return tuple(reversed(missing))
