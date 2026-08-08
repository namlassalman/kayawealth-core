"""Generate the simulated, metadata-rich AuraWealth knowledge corpus."""

import json
import os


TOPICS = [
    (
        "tax_planning", "Regional Tax Optimisation Guidelines for High-Net-Worth Individuals",
        ["a client is deciding whether to realise a capital gain before a move", "a family is comparing tax-aware giving with a cash gift", "a business owner needs to separate company and personal cash flows", "a client asks how investment income affects their annual tax position", "a couple is planning withdrawals across accounts with different tax treatment"],
        ["tax residency, source of income, and timing assumptions", "available reliefs, account ownership, and supporting records", "professional tax advice before executing a transaction", "whether the proposed action changes liquidity or concentration risk", "the difference between an illustration and a tax filing position"],
    ),
    (
        "risk_management", "Equities Volatility Benchmarks and Drawdown Mitigation Protocols",
        ["a growth portfolio falls 12% during a volatile month", "a client says they want higher returns but is uneasy about losses", "a concentrated employer-stock position dominates household wealth", "a near-term property purchase reduces the time available to recover losses", "a client wants to compare a stress scenario with their stated risk tolerance"],
        ["capacity for loss, investment horizon, and emergency liquidity", "maximum drawdown assumptions and the client’s behavioural response", "concentration, correlation, and diversification trade-offs", "whether existing insurance or debt changes overall resilience", "documented suitability evidence before any portfolio change"],
    ),
    (
        "portfolio_rebalancing", "Strategic Asset Allocation and Quarterly Rebalancing Frameworks",
        ["equity weights drift above the approved strategic allocation", "new savings need to be invested without increasing a concentrated holding", "a client requests a growth-portfolio rebalance after a market rally", "withdrawals are required while preserving a long-term allocation", "an advisor is reviewing quarterly drift against agreed target ranges"],
        ["target weights, drift bands, transaction costs, and taxes", "liquidity needs before selling long-term investments", "whether rebalancing is suitable for the client’s risk profile", "the difference between strategic allocation and a short-term market call", "PENDING_REVIEW approval before a client receives an actionable trade plan"],
    ),
    (
        "fixed_income", "Fixed-Income Duration, Credit, and Laddering Playbook",
        ["interest rates rise and a client asks why bond prices moved", "a client needs predictable cash flow over the next three years", "a portfolio has credit exposure that may not suit a cautious investor", "an investor compares a bond ladder with holding additional cash", "a client asks how duration changes sensitivity to rate moves"],
        ["duration, credit quality, maturity dates, and issuer concentration", "cash-flow timing and the possibility of selling before maturity", "inflation risk and reinvestment risk", "whether yield is being confused with guaranteed return", "suitability review before changing income allocations"],
    ),
    (
        "estate_planning", "Cross-Border Wealth Transfer, Trusts, and Intergenerational Governance",
        ["a client wants to update beneficiaries after a family change", "assets are held across more than one jurisdiction", "a parent wants to discuss a staged inheritance for adult children", "a family business needs continuity planning alongside investment assets", "a client asks how a trust differs from a will"],
        ["asset ownership, beneficiary designations, and jurisdiction", "the role of legal advice and up-to-date estate documents", "liquidity for expenses, taxes, and dependants", "family governance and communication risks", "the limits of general financial guidance"],
    ),
    (
        "alternative_assets", "Private Markets, Real Estate, and Alternative-Asset Exposure Limits",
        ["a client considers a private-equity fund with a long lock-up", "commercial-property exposure is already significant through a family business", "an investor asks whether private credit improves diversification", "a client wants venture-capital exposure after seeing recent headlines", "a portfolio review identifies illiquid holdings that are difficult to value"],
        ["lock-up period, valuation uncertainty, fees, and liquidity", "correlation with existing business, property, or equity exposure", "the possibility of loss and limited secondary-market access", "whether the client can meet commitments during a downturn", "suitability and advisor approval before an allocation change"],
    ),
    (
        "liquidity_management", "Cash Reserves, Short-Term Goals, and Treasury-Ladder Planning",
        ["a client needs funds for a home deposit within 18 months", "an emergency reserve is below the client’s stated comfort level", "cash is accumulating after a business sale", "upcoming education costs need to be separated from long-term investments", "a client asks whether a short-term treasury ladder suits a known expense"],
        ["time horizon, amount, currency, and certainty of the liability", "deposit protection limits and issuer diversification", "access to funds during an emergency", "inflation trade-offs between cash and longer-term assets", "the difference between liquidity planning and return seeking"],
    ),
    (
        "sustainable_investing", "Sustainable-Investing Preferences and Portfolio Screening Framework",
        ["a client wants to exclude selected sectors from their portfolio", "an investor asks how an ESG screen can change diversification", "a family wants investments aligned with a climate-transition preference", "a client asks whether impact reporting proves financial performance", "an advisor compares broad-market exposure with a sustainability tilt"],
        ["the client’s stated values, exclusions, and prioritised outcomes", "tracking error, concentration, and benchmark trade-offs", "fund methodology and the limits of issuer sustainability data", "fees and availability of suitable diversified options", "whether the preference changes the approved risk profile"],
    ),
    (
        "regulatory_compliance", "Client Suitability, Financial-Crime, and Advisory Conduct Controls",
        ["a proposed portfolio action requires evidence of client suitability", "a client’s source-of-funds information needs refresh", "an advisor must distinguish education from a personalised recommendation", "a cross-border client request requires jurisdictional review", "a recommendation is rejected because required disclosures are incomplete"],
        ["identity and source-of-wealth checks where required", "risk-profile currency, mandate limits, and approval records", "clear disclosures, conflicts, and communication boundaries", "escalation to compliance when information is incomplete", "a human reviewer for client-specific portfolio changes"],
    ),
    (
        "macro_economics", "Inflation, Interest-Rate, and Global Growth Scenario Guide",
        ["central-bank interest rates are expected to remain higher for longer", "inflation surprises change the purchasing power of retirement income", "global growth slows while equity-market valuations remain elevated", "a client asks why currency movements affect an overseas fund", "a rate cut is announced and the client wants to understand possible bond effects"],
        ["the distinction between a scenario and a market forecast", "duration, inflation sensitivity, currency exposure, and diversification", "how macro conditions interact with the client’s time horizon", "whether short-term headlines are driving an unsuitable portfolio change", "the need for a suitability review before acting on a macro view"],
    ),
    (
        "retirement_planning", "Retirement Income, Pension Drawdown, and Longevity Planning",
        ["a client wants to retire in 15 years and replace part of their salary", "a household needs to estimate sustainable income after work", "a pension drawdown decision must account for inflation and longevity", "a client asks how to sequence cash, bonds, and equities in early retirement", "a planned career break changes the savings path toward financial independence"],
        ["desired spending, other income, and realistic savings assumptions", "retirement age, longevity range, inflation, and healthcare costs", "withdrawal sequencing and the risk of poor early market returns", "emergency reserves and insurance protection before changing investments", "advisor review before presenting a personalised retirement recommendation"],
    ),
    (
        "insurance_protection", "Insurance Protection, Health Coverage, and Family Resilience Planning",
        ["a family wants to assess income protection after the birth of a child", "a client’s mortgage creates a temporary life-insurance need", "healthcare costs are a concern while planning for retirement", "a self-employed client wants to understand business-continuity protection", "a household is reviewing whether existing cover still matches dependants"],
        ["income replacement needs, debt, dependants, and existing cover", "policy exclusions, waiting periods, affordability, and renewal risk", "the difference between insurance protection and investment performance", "coordination with emergency reserves and estate documents", "referral to a licensed specialist where regulated advice is required"],
    ),
]

CLUSTER_CENTERS = {
    "tax_planning": (-4.0, 3.0), "risk_management": (-1.5, 3.0),
    "portfolio_rebalancing": (1.5, 3.0), "fixed_income": (4.0, 3.0),
    "estate_planning": (-4.0, -1.0), "alternative_assets": (-1.5, -1.0),
    "liquidity_management": (1.5, -1.0), "sustainable_investing": (4.0, -1.0),
    "regulatory_compliance": (-1.5, -5.0), "macro_economics": (1.5, -5.0),
    "retirement_planning": (-4.0, -5.0), "insurance_protection": (4.0, -5.0),
}


def generate_1200_chunks() -> None:
    """Create 100 varied simulated passages per wealth-management topic."""
    print("Generating the AuraWealth simulated knowledge corpus...")
    chunks_corpus = []
    chunks_per_doc = 100

    for doc_id, (category, title, scenarios, review_points) in enumerate(TOPICS, 1):
        for index in range(chunks_per_doc):
            scenario = scenarios[index % len(scenarios)]
            review_point = review_points[(index // len(scenarios)) % len(review_points)]
            centre_x, centre_y = CLUSTER_CENTERS[category]
            year = 2024 if index % 2 == 0 else 2026
            text = (
                f"Simulated internal education note — {title}. "
                f"Client scenario: {scenario}. "
                f"Advisor discussion should test {review_point}. "
                f"Use this material for guided discovery and record assumptions; it is not a client-specific "
                f"recommendation or a promise of investment outcome."
            )
            chunks_corpus.append({
                "id": f"doc_{doc_id}_chunk_{index}",
                "document_title": title,
                "category": category,
                "text": text,
                "chunk_index": index,
                "recency_year": year,
                "cluster_x": round(centre_x + ((index % 10) - 4.5) * 0.12, 2),
                "cluster_y": round(centre_y + ((index // 10) - 4.5) * 0.12, 2),
            })

    output_path = os.path.join(os.path.dirname(__file__), "kb_chunks.json")
    with open(output_path, "w") as file:
        json.dump(chunks_corpus, file, indent=4)
    print(f"Generated {len(chunks_corpus)} simulated chunks at {output_path}")


if __name__ == "__main__":
    generate_1200_chunks()
