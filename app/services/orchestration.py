"""Intent routing and advisor-policy conflict detection for issue #29."""


def select_workflow(user_query: str) -> str:
    query = user_query.lower()
    if any(phrase in query for phrase in (
        "what is this platform", "what is this platofrm", "what is aurawealth",
        "what is this app", "what is this application", "what is this for",
        "platform purpose", "application used for", "get rich", "make me rich", "be rich",
    )):
        return "client_guidance"
    if any(term in query for term in ("search", "what does", "policy", "compliance", "document", "guideline")):
        return "rag_search"
    if any(term in query for term in ("feedback", "correction", "clarify", "previous response")):
        return "feedback_aware_agents"
    return "sequential_agents"


def detect_advisor_conflict(user_query: str, critiques: list[str]) -> str | None:
    """Flag a high-risk client request that conflicts with a recorded advisor mandate."""
    client_requests_high_risk = any(term in user_query.lower() for term in ("high-risk", "aggressive", "speculative"))
    advisor_requires_low_volatility = any(
        any(term in critique.lower() for term in ("low-volatility", "low volatility", "conservative mandate", "reduce risk"))
        for critique in critiques
    )
    if client_requests_high_risk and advisor_requires_low_volatility:
        return "Client high-risk request conflicts with a recorded advisor low-volatility mandate."
    return None
