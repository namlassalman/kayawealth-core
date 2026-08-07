# Task 27 — Content Testing Results

## Reproducible board scenarios

| Role | Action | Expected result | Automated evidence |
| --- | --- | --- | --- |
| Client | Submit `Run agent simulation for my retirement account.` | A `PENDING_REVIEW` message is shown and the raw recommendation is withheld. | `test_client_guidance_and_retirement_simulation_governance` verifies `client_delivery_blocked=True`. |
| Wealth Advisor | Open the pending record, add `Reduce international equity exposure by 5%.`, then reject. | The report is not delivered; correction notes are persisted to `feedback_logs.json`. | `test_portfolio_recommendation_is_persisted_and_blocked_until_approved` verifies the persisted decision lifecycle; frontend review panel requires notes for rejection. |
| Compliance Auditor | Search `tax` and filter by 2026 in the Hybrid Search sidebar. | Fresh 2026 chunks rank first with a rerank score of 1.5. | `test_search_service_hybrid_deduplicates_and_reranks_recent_chunks` verifies the top score is 1.5. |

## Presentation defects fixed

- Plain-language onboarding queries now receive a client-facing explanation of AuraWealth as a financial GPS.
- Broad ambitions such as `get rich` now begin a financially literate goal-discovery conversation and avoid return guarantees.
- Retirement simulation requests are classified as portfolio-action workflows and are review-gated.
- The client title, quick actions, and suggested prompts now communicate the product purpose before the first message.
