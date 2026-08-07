"""Session-scoped dialogue focus tracking for issue #2."""

from dataclasses import asdict, dataclass


@dataclass
class DialogueState:
    focus: str = "general_advice"
    previous_focus: str | None = None
    turn_count: int = 0
    transition: str | None = None

    def payload(self) -> dict:
        return asdict(self)


def infer_focus(user_query: str) -> str:
    query = user_query.lower()
    if any(term in query for term in ("purpose", "onboard", "getting started", "what is this")):
        return "onboarding"
    if any(term in query for term in ("rebalance", "allocation", "portfolio change")):
        return "rebalancing"
    if any(term in query for term in ("risk", "volatility", "drawdown", "exposure")):
        return "risk_assessment"
    return "general_advice"


def update_dialogue_state(state: DialogueState | None, user_query: str) -> DialogueState:
    current = state or DialogueState()
    next_focus = infer_focus(user_query)
    current.transition = None
    if current.turn_count and next_focus != current.focus:
        current.previous_focus = current.focus
        current.transition = f"{current.focus} -> {next_focus}"
    current.focus = next_focus
    current.turn_count += 1
    return current
