"""Verify that a subtree-split skill exactly matches its authoritative source."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


class DistributionError(ValueError):
    """Raised when a distributed skill is incomplete or contains extra files."""


_RESOURCE_LINK = re.compile(
    r"\((?P<path>(?:references|scripts|assets)/[^)#?\s]+)(?:[?#][^)]*)?\)"
)
_REQUIRED_FILES = {"SKILL.md", "agents/openai.yaml"}


def _files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def _declared_resources(skill_md: Path) -> set[str]:
    content = skill_md.read_text(encoding="utf-8")
    return {match.group("path") for match in _RESOURCE_LINK.finditer(content)}


def _format_paths(paths: set[str]) -> str:
    return ", ".join(sorted(paths))


def check_distribution(source: Path, distribution: Path) -> None:
    """Require identical files and bytes at the distribution branch root."""
    source = source.resolve()
    distribution = distribution.resolve()
    source_files = _files(source)
    distribution_files = _files(distribution)

    missing_required = _REQUIRED_FILES - source_files
    if missing_required:
        raise DistributionError(
            f"source missing required files: {_format_paths(missing_required)}"
        )

    declared = _declared_resources(source / "SKILL.md")
    for resource in sorted(declared):
        if resource not in source_files:
            raise DistributionError(f"missing declared resource in source: {resource}")
        if resource not in distribution_files:
            raise DistributionError(
                f"missing declared resource in distribution: {resource}"
            )

    missing = source_files - distribution_files
    if missing:
        raise DistributionError(f"missing files: {_format_paths(missing)}")
    unexpected = distribution_files - source_files
    if unexpected:
        raise DistributionError(f"unexpected files: {_format_paths(unexpected)}")

    changed = {
        relative
        for relative in source_files
        if (source / relative).read_bytes() != (distribution / relative).read_bytes()
    }
    if changed:
        raise DistributionError(f"different content: {_format_paths(changed)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="check that a distributed skill exactly matches its source tree"
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("distribution", type=Path)
    args = parser.parse_args()
    try:
        check_distribution(args.source, args.distribution)
    except DistributionError as exc:
        parser.error(str(exc))
    print("Skill distribution matches its authoritative source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
