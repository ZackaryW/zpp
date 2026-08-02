import questionary

from zpp.utils.agent_selection import select_agents
from zpp.utils.models import CancelledAgentSelection, ConfirmedAgentSelection


def test_agent_selection_distinguishes_empty_submission_from_cancellation(
    monkeypatch,
) -> None:
    offered: list[list[str]] = []
    answers = iter(([], None))

    class Prompt:
        def ask(self):
            return next(answers)

    def checkbox(_message: str, *, choices: list[str]):
        offered.append(choices)
        return Prompt()

    monkeypatch.setattr(questionary, "checkbox", checkbox)

    submitted = select_agents(("pi", "codex", "claude"))
    cancelled = select_agents(("pi", "codex", "claude"))

    assert submitted == ConfirmedAgentSelection(())
    assert isinstance(cancelled, CancelledAgentSelection)
    assert offered == [["pi", "codex", "claude"], ["pi", "codex", "claude"]]
