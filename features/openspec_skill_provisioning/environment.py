def before_scenario(context, scenario):
    context.zpp_capability = "openspec_skill_provisioning"


def after_scenario(context, scenario):
    home = getattr(context, "home", None)
    if home is not None:
        home.close()
