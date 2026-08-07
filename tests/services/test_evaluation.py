from app.services.evaluation import evaluate_response


def test_golden_evaluation_detects_missing_signals():
    assert evaluate_response("retirement_risk", "Risk Assessment complete. Next Step: advisor review.")["verdict"] == "PASS"
    assert evaluate_response("retirement_risk", "Guaranteed return.")["verdict"] == "FAIL"
