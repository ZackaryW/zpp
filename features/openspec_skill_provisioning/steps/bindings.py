from features.support.bindings import register_exact_steps

register_exact_steps(
    (
        "the local OpenSpec CLI generates its canonical operation skills",
        "a user selects one or more supported agents",
        "the user runs zpp init",
        "ZPP validates every selected agent OpenSpec inventory before projection",
        "Agent Router installs the workflow skill native hook and six OpenSpec skills "
        "for each selected agent",
        "each generated skill records the detected OpenSpec version as ZPP provenance",
        "the local OpenSpec CLI fails or returns an unexpected inventory for one "
        "selected agent",
        "the user runs zpp init for several agents",
        "no selected agent workflow hook or skill is projected",
        "the generation failure remains visible",
        "Agent Router owns an earlier generated OpenSpec skill",
        "the detected OpenSpec version or generated content changes",
        "the user runs zpp init again",
        "ZPP freshly generates every selected agent inventory",
        "Agent Router safely reconciles the changed owned skill",
        "a user selects a supported agent and integration scope",
        "the user inspects or invokes workflow install update or remove",
        "only the consolidated workflow skill and native hook are managed",
        "no OpenSpec lifecycle option is exposed",
        "every standard user integration passes complete reset preflight",
        "a canonical OpenSpec skill is modified but validly owned by Agent Router",
        "a user runs zpp reset with confirmation",
        "Agent Router force-deletes every present canonical OpenSpec skill and "
        "ownership record",
        "no removed OpenSpec backup or history is retained",
        "OpenSpec generation is not invoked",
        "one or more canonical OpenSpec skills and ownership records are absent",
        "absent generated skills are treated as converged no-ops",
        "OpenLease state is replaced after all removals succeed",
        "a canonical OpenSpec skill is present without matching Agent Router ownership",
        "Agent Router refuses to delete the unmanaged skill",
        "reset leaves prior OpenLease state unchanged",
    )
)
