def before_scenario(context, scenario):
    context.zpp_capability = "workflow_coordination_bypass"


def after_scenario(context, scenario):
    environment = getattr(context, "environment", None)
    if environment is not None:
        environment.close()
