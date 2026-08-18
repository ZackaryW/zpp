def before_scenario(context, scenario):
    context.zpp_capability = "repository_trait_bootstrap"


def after_scenario(context, scenario):
    for attribute in ("repository", "coordination"):
        subject = getattr(context, attribute, None)
        if subject is not None:
            subject.close()
