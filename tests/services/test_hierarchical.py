import asyncio

from app.services.hierarchical import run_hierarchical_workflow


def test_manager_delegates_portfolio_review_to_three_specialists():
    result = asyncio.run(run_hierarchical_workflow("Review portfolio allocation"))
    assert result["manager_route"] == "portfolio_review"
    assert result["delegated_agents"] == ["intake", "risk", "portfolio"]
