from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from zpp.utils.models import ManagedStateError


WORKFLOW_SKILL_NAMES = (
    "zpp-clarify-change",
    "zpp-commit-zmem",
    "zpp-form-specs",
    "zpp-mature-utilities",
    "zpp-plan-utilities",
    "zpp-reconcile-codespace-worktrees",
    "zpp-shape-feature",
    "zpp-wire-feature",
)
SKILL_MANIFEST_NAME = ".zpp-workflow-skills.json"


@dataclass(frozen=True, slots=True)
class SkillFile:
    relative_path: str
    content: bytes


@dataclass(frozen=True, slots=True)
class SkillBundle:
    version: str
    files: tuple[SkillFile, ...]
    fingerprint: str


class SkillBundleManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    bundle_version: str = Field(min_length=1)
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
                or relative.parts[0] not in WORKFLOW_SKILL_NAMES
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError(f"invalid owned skill path or digest: {path}")
        return value

    @model_validator(mode="after")
    def require_skill_documents(self) -> SkillBundleManifest:
        required = {f"{name}/SKILL.md" for name in WORKFLOW_SKILL_NAMES}
        if not required.issubset(self.files):
            raise ValueError("manifest does not own every permanent SKILL.md")
        return self


@dataclass(frozen=True, slots=True)
class SkillProjectionInspection:
    root: Path
    state: Literal["absent", "compatible", "outdated", "conflict"]
    version: str | None = None
    manifest: SkillBundleManifest | None = None
    reason: str | None = None
    scope: Literal["local", "global"] | None = None
    agents: tuple[str, ...] = ()


def fingerprint_skill_files(files: Iterable[SkillFile]) -> str:
    digest = sha256()
    for file in sorted(files, key=lambda item: item.relative_path):
        path = file.relative_path.encode("utf-8")
        digest.update(len(path).to_bytes(8, "big"))
        digest.update(path)
        digest.update(len(file.content).to_bytes(8, "big"))
        digest.update(file.content)
    return digest.hexdigest()


def collect_skill_bundle(root: Traversable, version: str) -> SkillBundle:
    children = tuple(root.iterdir())
    names = tuple(sorted(child.name for child in children))
    if names != WORKFLOW_SKILL_NAMES or any(not child.is_dir() for child in children):
        raise ValueError("workflow skill bundle must contain exactly the permanent skills")

    collected: list[SkillFile] = []
    for child in sorted(children, key=lambda item: item.name):
        if _is_symlink(child):
            raise ValueError(f"workflow skill bundle contains a symlink: {child.name}")
        document = child.joinpath("SKILL.md")
        if not document.is_file() or _is_symlink(document):
            raise ValueError(f"workflow skill {child.name} is missing SKILL.md")
        try:
            document.read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(
                f"workflow skill {child.name} SKILL.md is not valid UTF-8"
            ) from error
        _collect_files(child, PurePosixPath(child.name), collected)

    bundle_files = tuple(sorted(collected, key=lambda item: item.relative_path))
    return SkillBundle(version, bundle_files, fingerprint_skill_files(bundle_files))


def load_packaged_skill_bundle(version: str) -> SkillBundle:
    return collect_skill_bundle(files("zpp.artifacts").joinpath("skills"), version)


def manifest_for_bundle(bundle: SkillBundle) -> SkillBundleManifest:
    return SkillBundleManifest(
        bundle_version=bundle.version,
        fingerprint=bundle.fingerprint,
        files={
            file.relative_path: sha256(file.content).hexdigest()
            for file in bundle.files
        },
    )


def load_skill_manifest(path: Path) -> SkillBundleManifest | None:
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise ManagedStateError(f"managed skill manifest is not a regular file: {path}")
    try:
        return SkillBundleManifest.model_validate_json(path.read_bytes())
    except (OSError, UnicodeError, ValidationError) as error:
        raise ManagedStateError(f"managed skill manifest is invalid: {path}") from error


def inspect_skill_projection(
    root: Path,
    expected: SkillBundle,
) -> SkillProjectionInspection:
    manifest_path = root / SKILL_MANIFEST_NAME
    claimed_paths = tuple(root / name for name in WORKFLOW_SKILL_NAMES)
    manifest_present = manifest_path.exists() or manifest_path.is_symlink()
    claimed_present = any(path.exists() or path.is_symlink() for path in claimed_paths)
    if not manifest_present:
        if claimed_present:
            return SkillProjectionInspection(root, "conflict", reason="unmanaged skill collision")
        return SkillProjectionInspection(root, "absent")

    try:
        manifest = load_skill_manifest(manifest_path)
        if manifest is None:
            raise ManagedStateError(f"managed skill manifest disappeared: {manifest_path}")
        actual = _read_projection_files(root)
    except (ManagedStateError, OSError, UnicodeError, ValueError) as error:
        return SkillProjectionInspection(root, "conflict", reason=str(error))

    if set(actual) != set(manifest.files):
        return SkillProjectionInspection(
            root,
            "conflict",
            manifest=manifest,
            reason="managed skill file set differs from its manifest",
        )
    if any(
        sha256(file.content).hexdigest() != manifest.files[file.relative_path]
        for file in actual.values()
    ):
        return SkillProjectionInspection(
            root,
            "conflict",
            manifest=manifest,
            reason="managed skill content differs from its manifest",
        )
    actual_fingerprint = fingerprint_skill_files(actual.values())
    if actual_fingerprint != manifest.fingerprint:
        return SkillProjectionInspection(
            root,
            "conflict",
            manifest=manifest,
            reason="managed skill fingerprint differs from its manifest",
        )

    state: Literal["compatible", "outdated"] = (
        "compatible"
        if manifest.bundle_version == expected.version
        and manifest.fingerprint == expected.fingerprint
        else "outdated"
    )
    return SkillProjectionInspection(
        root,
        state,
        version=manifest.bundle_version,
        manifest=manifest,
    )


def _collect_files(
    node: Traversable,
    relative: PurePosixPath,
    collected: list[SkillFile],
) -> None:
    for child in sorted(node.iterdir(), key=lambda item: item.name):
        if _is_symlink(child):
            raise ValueError(f"workflow skill bundle contains a symlink: {relative / child.name}")
        child_relative = relative / child.name
        if child.is_dir():
            _collect_files(child, child_relative, collected)
        elif child.is_file():
            collected.append(SkillFile(child_relative.as_posix(), child.read_bytes()))
        else:
            raise ValueError(f"workflow skill bundle contains an invalid entry: {child_relative}")


def _is_symlink(node: Traversable) -> bool:
    return isinstance(node, Path) and node.is_symlink()


def _read_projection_files(root: Path) -> dict[str, SkillFile]:
    if root.is_symlink() or not root.is_dir():
        raise ManagedStateError(f"managed skill root is not a regular directory: {root}")
    result: dict[str, SkillFile] = {}
    for name in WORKFLOW_SKILL_NAMES:
        skill = root / name
        if skill.is_symlink() or not skill.is_dir():
            raise ManagedStateError(f"managed skill directory is invalid: {skill}")
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise ManagedStateError(f"managed skill content contains a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(root).as_posix()
                result[relative] = SkillFile(relative, path.read_bytes())
            elif not path.is_dir():
                raise ManagedStateError(f"managed skill content is invalid: {path}")
    return result
