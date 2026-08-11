from __future__ import annotations

from zpp.core.models import ResolutionResult

_BODY_SEPARATOR = "\n\n---\n\n"


def render_prompt_bodies(result: ResolutionResult) -> str:
    return _BODY_SEPARATOR.join(
        body for family in result.families for body in family.bodies
    )
