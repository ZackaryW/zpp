from __future__ import annotations

from zpp.utils.models import ZppValidationError


class ZppDomainError(ValueError):
    """A user-facing domain or managed-state rejection."""


def validation_diagnostic(error: ZppValidationError) -> str:
    lines: list[str] = []
    for issue in error.issues:
        subject = str(issue.source) if issue.source is not None else "ZPP state"
        location = ".".join(str(part) for part in issue.location)
        suffix = f" ({location})" if location else ""
        lines.append(f"{subject}{suffix}: {issue.message}")
    return "\n".join(lines)
