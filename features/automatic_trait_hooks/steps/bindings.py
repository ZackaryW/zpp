from behave import step

from features.support.bindings import register_exact_steps
from features.support.lifecycle import record_step


@step("ZPP packages the {agent} workflow integration")
def package_agent_integration(context, agent):
    record_step(context, f"ZPP packages the {agent} workflow integration")


@step("the hook uses the {event} context injection form")
def use_native_event(context, event):
    record_step(context, f"the hook uses the {event} context injection form")


@step("it resolves the current repository with {agent} as the invoking agent")
def resolve_for_agent(context, agent):
    record_step(
        context,
        f"it resolves the current repository with {agent} as the invoking agent",
    )


register_exact_steps(
    (
        "Agent Router inspects its native hook",
        "a user selects a supported agent and integration scope",
        "ZPP installs the workflow integration",
        "Agent Router projects one consolidated workflow skill",
        "Agent Router projects that agent native trait hook",
        "Agent Router owns an intact ZPP workflow skill and native trait hook",
        "a user removes that workflow integration",
        "Agent Router removes both assets from the selected scope",
        "an installed native hook starts in a repository with active traits",
        "its public resolver command succeeds",
        "the hook injects the returned complete bodies as advisory environment policy",
        "it does not select execute or complete a workflow stage",
        "an installed native hook starts in a repository",
        "its public resolver command fails",
        "the failure remains visible through the native hook contract",
        "no partial stale or cached trait body is injected as successful context",
    )
)
