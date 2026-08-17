def before_scenario(context, scenario):
    context.zpp_capability = "automatic_trait_hooks"


def after_scenario(context, scenario):
    project = getattr(context, "project", None)
    if project is not None:
        project.close()
