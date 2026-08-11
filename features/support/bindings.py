from __future__ import annotations

from collections.abc import Sequence

from behave import step

from features.support.lifecycle import record_step


def register_exact_steps(phrases: Sequence[str]) -> None:
    for phrase in phrases:
        step(phrase)(_recorder(phrase))


def _recorder(phrase: str):
    def record(context) -> None:
        record_step(context, phrase)

    return record
