def before_scenario(context, scenario):
    context.zpp_capability = "automatic_trait_hooks"


def after_scenario(context, scenario):
    for attribute in ("project", "coordination", "repository"):
        subject = getattr(context, attribute, None)
        if subject is not None:
            subject.close()
