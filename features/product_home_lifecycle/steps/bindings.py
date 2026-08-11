from features.support.bindings import register_exact_steps

register_exact_steps(
    (
        "a caller selects an eligible ZPP home",
        "an OpenLease-backed ZPP command runs",
        "ZPP uses only that home's openlease child as managed state",
        "selecting the home alone creates no directory",
        "the selected eligible ZPP home is absent",
        "a user runs zpp open",
        "ZPP creates and natively opens that exact home",
        "it reports the resolved home without initializing the openlease child",
        "user integrations and OpenLease state may exist",
        "a user runs zpp reset without confirmation",
        "ZPP rejects the command before inspecting or changing external state",
        "every supported agent user integration is absent or ownership-safe removable",
        "the selected ZPP home and its openlease child are safe",
        "a user runs zpp reset with confirmation",
        "ZPP removes every present user workflow skill hook and generated OpenSpec "
        "operation skill through Agent Router",
        "ZPP replaces only the selected home's openlease child with fresh state",
        "repository project plugin worktree and other home contents remain unchanged",
        "confirmed reset can complete against safe user integrations and state",
        "the user runs confirmed reset with and without JSON output",
        "the default reset result is one concise line with removal and state outcomes",
        "the JSON reset result retains complete inspection removal and state details",
        "one supported agent user workflow skill or hook conflicts with its "
        "packaged asset",
        "ZPP identifies the conflicting agent integration",
        "no user workflow integration or OpenLease state is changed",
        "complete reset preflight succeeds",
        "one Agent Router integration removal fails",
        "ZPP attempts every preflighted removal and reports their outcomes",
        "the prior OpenLease state remains unchanged",
        "a retry accepts already absent integrations and can complete the reset",
        "the selected home or openlease child cannot be proven to be a safe "
        "directory boundary",
        "ZPP fails before changing an agent integration or filesystem path",
    )
)
