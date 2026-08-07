"""Alternative manager-led workflow for issue #7."""

import asyncio


def select_delegation_plan(user_query: str) -> tuple[str, list[str]]:
    query = user_query.lower()
    if any(term in query for term in ("rebalance", "allocation", "portfolio")):
        return "portfolio_review", ["intake", "risk", "portfolio"]
    if any(term in query for term in ("risk", "volatility", "drawdown")):
        return "risk_review", ["intake", "risk"]
    return "comprehensive_review", ["intake", "risk", "portfolio"]


async def intake_specialist(user_query: str) -> str:
    await asyncio.sleep(0.05)
    return f"Client objective captured: {user_query}"


async def risk_specialist(intake_summary: str) -> str:
    await asyncio.sleep(0.05)
    return f"Risk review completed against internal suitability thresholds. Context: {intake_summary}"


async def portfolio_specialist(risk_summary: str) -> str:
    await asyncio.sleep(0.05)
    return f"Portfolio specialist prepared an advisor-review recommendation. Context: {risk_summary}"


async def run_hierarchical_workflow(user_query: str) -> dict:
    """Manager selects specialists, delegates work, and consolidates a single response."""
    manager_route, delegated_agents = select_delegation_plan(user_query)
    intake = await intake_specialist(user_query)
    risk = await risk_specialist(intake)
    portfolio = await portfolio_specialist(risk) if "portfolio" in delegated_agents else "Portfolio delegation not required for this request."

    return {
        "manager_route": manager_route,
        "delegated_agents": delegated_agents,
        "final_report": (
            "### 👑 AuraWealth Manager Consolidated Report\n\n"
            f"* **Client Objective:** {user_query}\n"
            f"* **Intake Specialist:** {intake}\n"
            f"* **Risk Specialist:** {risk}\n"
            f"* **Portfolio Specialist:** {portfolio}\n\n"
            "**Next Step:** Submit this consolidated view for advisor review before any portfolio action."
        ),
    }
