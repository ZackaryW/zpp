from behave import step

from features.support.bindings import register_exact_steps
from features.support.lifecycle import record_step

register_exact_steps(
    (
        "an unregistered Git worktree has no zpp.behave.yaml",
        "a user runs zpp behave init from within that worktree",
        "ZPP initializes a root version-one YAML mapping with empty commands through "
        "zpp.behave",
        "it reports provider diagnostics without creating OpenLease topology or a "
        "space",
        "a repository has a valid authored version-one zpp.behave.yaml",
        "a user runs zpp behave init",
        "ZPP validates the dedicated root mapping without wrapping or rewriting it",
        "provider discovery changes only the reported machine-local diagnostics",
        "a behavior mapping contains an unsafe path duplicate target value invalid "
        "gate or unknown field",
        "a user selects one of its commands",
        "ZPP rejects the complete mapping before starting a configured process",
        "no legacy behavior implementation runs as fallback",
        "a command declares several ordered targets with repository path rules",
        "every changed path maps conclusively to a proper subset",
        "a user runs that command without a selection override",
        "ZPP submits only the affected declared target values in declaration order",
        "a command declares several verification targets",
        "at least one changed path is invalid unmapped or uncertain",
        "ZPP performs default affected selection",
        "every target declared by the selected command is submitted",
        "a valid command and mapping are selected",
        "repository evidence contains no changed path",
        "it reports that no target is affected",
        "it starts no provider process",
        "a command declares ordered targets and a valid command-local gate",
        "a user selects exact targets a gate all targets or a paired revision range",
        "ZPP applies only that requested selection mode",
        "repeated exact targets are submitted once in declaration order",
        "a valid behavior command is available",
        "a user combines selection modes or supplies only one revision endpoint",
        "ZPP rejects the invocation before process creation",
        "it does not fall back to affected or complete execution",
        "ZPP submits the selected declared target values",
        "ZPP does not infer install download or select another provider",
        "zpp.behave registers its supported reconciliation callbacks",
        "a repository contains zpp.behave.yaml",
        "reconciliation selects no behavior callback",
        "no behavior command is invoked",
        "the selection names its behavior command selection mode and target context",
        "OpenLease invokes the callback against the real reconciliation context",
        "ZPP resolves the exact target repository mapping and returns the configured "
        "outcome",
        "reconciliation selects a behavior callback",
        "its command selection mode event mode or required target context is absent",
        "OpenLease rejects the callback plan instead of guessing repository policy",
    )
)


@step(
    "a command selects the valid {provider} provider and its required surface is "
    "available"
)
def select_provider(context, provider):
    record_step(
        context,
        f"a command selects the valid {provider} provider and its required surface "
        "is available",
    )


@step("the {provider} adapter constructs one validated shell-free argument sequence")
def construct_provider_arguments(context, provider):
    record_step(
        context,
        f"the {provider} adapter constructs one validated shell-free argument sequence",
    )


@step(
    "reconciliation explicitly selects a valid zpp.behave {event} callback in "
    "{mode} mode"
)
def select_callback(context, event, mode):
    record_step(
        context,
        f"reconciliation explicitly selects a valid zpp.behave {event} callback in "
        f"{mode} mode",
    )
