"""Client-facing intent responses kept separate from advisor workflow reports."""


def client_guidance_response(user_query: str) -> str | None:
    """Return a warm, non-advisory response for onboarding and goal discovery."""
    query = user_query.lower().strip()

    if any(phrase in query for phrase in (
        "what is this platform", "what is this platofrm", "what is aurawealth",
        "what is this app", "what is this application", "what is this for",
        "platform purpose", "application used for",
    )):
        return (
            "### Welcome to AuraWealth 👋\n\n"
            "AuraWealth is your **financial GPS**: one place to understand your overall financial picture, "
            "turn life ambitions into practical goals, and work transparently with a wealth advisor when a "
            "portfolio decision needs review.\n\n"
            "We can start with something simple: retirement planning, building an emergency fund, reducing debt, "
            "or understanding investment risk. What would you most like your money to help you do?"
        )

    if any(phrase in query for phrase in ("get rich", "make me rich", "be rich")):
        return (
            "Wanting more financial freedom is a useful starting point. Building wealth is **not a guaranteed outcome**, "
            "so let’s turn that ambition into a plan you can evaluate.\n\n"
            "To begin, tell me: **(1)** your timeframe, **(2)** a target amount or lifestyle goal, **(3)** how much you "
            "can save or invest each month, and **(4)** whether market ups and downs would make you uncomfortable.\n\n"
            "For example: “I want to build a $100,000 house deposit in five years and can save $1,200 a month.”"
        )

    return None
