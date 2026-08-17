def before_scenario(context, scenario):
    context.zpp_capability = "behavior_verification"


def after_scenario(context, scenario):
    repository = getattr(context, "repository", None)
    if repository is not None:
        repository.close()
