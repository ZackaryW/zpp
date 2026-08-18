def before_scenario(context, scenario):
    context.zpp_capability = "product_home_lifecycle"


def after_scenario(context, scenario):
    for attribute in ("env", "coordination"):
        subject = getattr(context, attribute, None)
        if subject is not None:
            subject.close()
