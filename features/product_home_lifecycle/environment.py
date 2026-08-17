def before_scenario(context, scenario):
    context.zpp_capability = "product_home_lifecycle"


def after_scenario(context, scenario):
    environment = getattr(context, "env", None)
    if environment is not None:
        environment.close()
