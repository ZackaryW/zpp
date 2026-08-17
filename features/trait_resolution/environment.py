def before_scenario(context, scenario):
    context.zpp_capability = "trait_resolution"


def after_scenario(context, scenario):
    workspace = getattr(context, "workspace", None)
    if workspace is not None:
        workspace.close()
