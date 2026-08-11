from __future__ import annotations


def begin_scenario(context, capability: str) -> None:
    context.zpp_capability = capability
    context.zpp_steps = []


def record_step(context, phrase: str) -> None:
    context.zpp_steps.append(phrase)


def verify_recorded_steps(context, scenario) -> None:
    expected = [step.name for step in scenario.all_steps]
    assert context.zpp_steps == expected
