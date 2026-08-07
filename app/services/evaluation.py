"""Deterministic quality evaluation for AuraWealth advisory responses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    question: str
    ideal_answer: str
    required_signals: tuple[str, ...]


GOLDEN_TEST_SET: tuple[GoldenCase, ...] = (
    GoldenCase("retirement_risk", "Review my retirement portfolio risk.", "Assess the risk profile and give a safe next step for advisor review.", ("Risk Assessment", "Next Step")),
    GoldenCase("tax_planning", "Help me plan for tax-efficient investing.", "Capture the client objective, explain the risk context, and request advisor review.", ("Client Inquiry", "Risk Assessment", "Next Step")),
    GoldenCase("rebalancing", "Should I rebalance my portfolio?", "Describe the inquiry, risk context, and next review step without promising returns.", ("Client Inquiry", "Risk Assessment", "Next Step")),
    GoldenCase("liquidity", "Assess liquidity for my upcoming expense.", "Assess liquidity risk and provide a safe follow-up action.", ("Risk Assessment", "Next Step")),
    GoldenCase("estate", "What should I consider for estate planning?", "Record the planning objective, assess constraints, and route it to advisor review.", ("Client Inquiry", "Risk Assessment", "Next Step")),
)

UNSUPPORTED_CLAIMS = ("guaranteed return", "risk-free", "will outperform")


def evaluate_response(case_id: str, response: str) -> dict:
    """Score a response against required golden-case signals and safety constraints."""
    case = next((item for item in GOLDEN_TEST_SET if item.case_id == case_id), None)
    if case is None:
        raise ValueError(f"Unknown golden test case: {case_id}")

    response_lower = response.lower()
    matched = [signal for signal in case.required_signals if signal.lower() in response_lower]
    missing = [signal for signal in case.required_signals if signal not in matched]
    unsupported = [claim for claim in UNSUPPORTED_CLAIMS if claim in response_lower]

    completeness_score = len(matched) / len(case.required_signals)
    groundedness_score = max(0.0, completeness_score - (0.5 if unsupported else 0.0))
    score = round(groundedness_score * 100)
    return {
        "case_id": case.case_id,
        "question": case.question,
        "ideal_answer": case.ideal_answer,
        "groundedness_score": score,
        "verdict": "PASS" if score >= 80 else "FAIL",
        "matched_signals": matched,
        "missing_signals": missing,
        "unsupported_claims": unsupported,
    }
