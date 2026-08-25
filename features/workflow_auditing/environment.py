def before_scenario(context, scenario):
    context.zpp_capability = "workflow_auditing"


def after_scenario(context, scenario):
    audit = getattr(context, "audit", None)
    if audit is not None:
        audit.close()
