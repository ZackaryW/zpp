from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType

from zpp.core.models import (
    EffectiveTraitFamily,
    EvidenceBranch,
    EvidenceRef,
    EvidenceResult,
)


@dataclass(frozen=True, slots=True)
class EvidenceRequest:
    ref: EvidenceRef
    branch: EvidenceBranch


@dataclass(frozen=True, slots=True)
class EvidenceRuntime:
    target: Path
    read_bytes: Callable[[Path], bytes]
    executable: Callable[[str], str | None]


def evidence_requests(
    families: Sequence[EffectiveTraitFamily],
) -> tuple[EvidenceRequest, ...]:
    return tuple(
        EvidenceRequest(
            EvidenceRef(
                family.family,
                flavor.effective_position,
                branch_position,
            ),
            branch,
        )
        for family in families
        for flavor in family.flavors
        for branch_position, branch in enumerate(flavor.flavor.when)
    )


def _digest(parts: Sequence[bytes]) -> str:
    digest = sha256()
    for part in parts:
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.hexdigest()


def _confined(target: Path, candidate: Path) -> Path | None:
    root = target.resolve()
    resolved = candidate.resolve()
    return resolved if resolved.is_relative_to(root) else None


def _workspace_observation(
    pattern: str,
    runtime: EvidenceRuntime,
) -> tuple[bool, str]:
    target = runtime.target.resolve()
    if pattern.startswith("/"):
        relative = pattern[1:]
        if any(marker in relative for marker in "*?["):
            matches = sorted(target.glob(relative))
        else:
            candidate = _confined(target, target / relative)
            matches = (
                [candidate] if candidate is not None and candidate.exists() else []
            )
    else:
        matches = sorted(target.glob(f"**/{pattern}"))
    confined = [item for item in matches if _confined(target, item) is not None]
    fingerprint_parts = [pattern.encode()]
    for path in confined:
        fingerprint_parts.append(str(path.relative_to(target)).encode())
        if path.is_file():
            try:
                fingerprint_parts.append(runtime.read_bytes(path))
            except OSError:
                fingerprint_parts.append(b"<unreadable>")
    return bool(confined), _digest(fingerprint_parts)


def _file_observation(
    path: str,
    literal: str,
    runtime: EvidenceRuntime,
) -> tuple[bool, str]:
    relative = path[1:] if path.startswith("/") else path
    candidate = _confined(runtime.target, runtime.target / relative)
    if candidate is None:
        return False, _digest([path.encode(), b"<outside>"])
    try:
        content = runtime.read_bytes(candidate)
    except OSError:
        content = b""
        readable = False
    else:
        readable = True
    needle = literal.encode()
    return readable and needle in content, _digest([path.encode(), needle, content])


def _which_observation(
    tool: str,
    runtime: EvidenceRuntime,
) -> tuple[bool, str, tuple[str, bool]]:
    located = runtime.executable(tool)
    available = located is not None
    fact_name = f"has_{tool.replace('-', '_')}"
    return (
        available,
        _digest([tool.encode(), (located or "<missing>").encode()]),
        (fact_name, available),
    )


def collect_evidence(
    branches: Sequence[EvidenceRequest],
    runtime: EvidenceRuntime,
) -> Mapping[EvidenceRef, EvidenceResult]:
    collected: dict[EvidenceRef, EvidenceResult] = {}
    for request in branches:
        matches: list[bool] = []
        facts: dict[str, bool] = {}
        fingerprints: dict[str, str] = {}
        branch = request.branch
        if branch.workspace_contains is not None:
            matched, fingerprint = _workspace_observation(
                branch.workspace_contains, runtime
            )
            matches.append(matched)
            fingerprints[f"workspace_contains:{branch.workspace_contains}"] = (
                fingerprint
            )
        if branch.file_contains is not None:
            matched, fingerprint = _file_observation(
                branch.file_contains.path,
                branch.file_contains.text,
                runtime,
            )
            matches.append(matched)
            fingerprints[
                f"file_contains:{branch.file_contains.path}:{branch.file_contains.text}"
            ] = fingerprint
        if branch.which is not None:
            matched, fingerprint, fact = _which_observation(branch.which, runtime)
            matches.append(matched)
            facts[fact[0]] = fact[1]
            fingerprints[f"which:{branch.which}"] = fingerprint
        collected[request.ref] = EvidenceResult(
            matched=bool(matches) and all(matches),
            facts=MappingProxyType(facts),
            fingerprints=MappingProxyType(fingerprints),
        )
    return MappingProxyType(collected)
