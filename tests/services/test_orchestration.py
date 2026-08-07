from app.services.orchestration import detect_advisor_conflict, select_workflow


def test_orchestration_routes_and_blocks_conflicting_mandates():
    assert select_workflow("What does the tax policy say?") == "rag_search"
    assert detect_advisor_conflict("Build an aggressive high-risk portfolio", ["Maintain a low-volatility mandate."])
