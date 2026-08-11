import support

from features.support.lifecycle import begin_scenario, verify_recorded_steps


def before_scenario(context, scenario):
    begin_scenario(context, "behavior_verification")


def after_scenario(context, scenario):
    verify_recorded_steps(context, scenario)
    support.verify()
