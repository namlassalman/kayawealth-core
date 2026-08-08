# AuraWealth Task Ledger

## Verified completion evidence

The rows below reconcile local implementation, tests, and atomic commits. “Done” means the committed prototype satisfies the stated local demonstration scope; linked remediation tasks capture known production or specification gaps.

| Issue | Local status | Commit evidence | Verification / follow-up |
| --- | --- | --- | --- |
| #1 | Done | `8d7b21f` | Sequential Intake → Risk → Report workflow. |
| #2 | Done | `b5f3158` | Dialogue-state tests pass. |
| #3 | Done (lexical prototype) | `9764ce8` | Metadata filters work; #33 tracks embeddings/vector remediation. |
| #4 | Done (lexical prototype) | `48c0f54` | Hybrid merge/deduplication works; #33 tracks vector remediation. |
| #5 | Done | `31cf02b` | 2026 chunks rank at 1.5; search tests pass. |
| #6 | Done | `b46aad3` | Cluster-map UI and tests pass; coordinates are simulated. |
| #7 | Done | `80c0cfd` | Manager-led hierarchy endpoint and tests pass. |
| #8 | Done | `cce7da1` | Deterministic critic/fallback; #37 tracks objective improvement proof. |
| #9 | Done | `4adca07` | Feedback capture persists locally; #37 tracks benchmark. |
| #10 | Done | `1ae11a6` | Local JSON history persistence; not authenticated session storage. |
| #11 | Done | `e5fe370` | Five-case deterministic groundedness evaluator and UI control. |
| #12 | Done | `576cfa1` | Regex prompt-injection guard tests pass. |
| #13 | Done | `fab8f49` | Pattern-based PII redaction tests pass. |
| #14 | Done | `23ef8cb` | Redis-backed recommendation review state; approval/rejection UI tested. |
| #15 | Done | `0690aec` | Advisor-only safe operational trace logs. |
| #16 | Done (standalone) | `cb517a5` | Mock tier-routing endpoints work; #35 tracks live-chat integration. |
| #17 | Done | `4f82b26` | Redis TTL cache with in-memory fallback. |
| #18 | Done | `a4df1eb` | Redis FIFO queue with local single consumer. |
| #19 | Done (baseline UI) | `465eeef` | Streamlit chat works; #31 tracks async transport. |
| #20 | Done | `d00bb30` | README diagram and claims reconciled to code. |
| #21 | Done (core scope) | `1c752be` | Async routes/background task exist; #32 tracks the separately scoped tick stream. |
| #22 | Done | `bc9e1d3` | 1,000 chunks from 10 simulated documents; #33 tracks >10-document/vector requirement. |
| #26 | Done | `e687810` | Search, UI, models, and services modularised. |
| #27 | Done | `9e44625` | Three content-test scenarios and fixes documented. |
| #28 | In Progress | `8547ed8` | `.env` profile loader exists; configuration audit remains. |
| #29 | Done | `83ab2c8` | Intent routing and mandate-conflict blocking. |
| #34 | Done | `23ef8cb` | Persisted `PENDING_REVIEW` workflow. |
| #36 | Done | `d00bb30` | Code-accurate README completed. |
| #39 | Done | `652a13b` | 19-test pytest quality gate. |

**Remote board note:** Reconciled on 2026-08-08. GitHub issues #7, #11, #12, and #13 are closed and their Project items are Done. Issue #38 is closed and its Project item is Done; the evidence note is recorded on the issue.

---

## [6] RAG: Embedding semantic clustering visual (+1)
* **Status:** Done
### Actions & Description:
Generate Scatter Coordinates: Group related data fragments into clusters based on shared themes.

Render Map Chart: Display a clean scatter-plot chart on the Streamlit dashboard to visually show the interviewer how the AI organizes documents.

Map Coordinate Matrices: Append static X/Y float positions to your 1,000 corporate data chunks to represent thematic cluster coordinates (e.g., matching tax planning to one spatial quadrant, risk management to another).

Render Chart Layer: Inject a native st.scatter_chart() component into the advisor sidebar layout to visually show the panel how the system organizes documents.

---

## [11] Governance: LLM-as-a-judge automated eval (+3)
* **Status:** Done
### Actions & Description:
Define Golden Test Set: Create a small mock list of 5 fixed "ideal answers" to standard financial questions.

Groundedness Scorer: Write an independent evaluation step that scores live AI answers against this golden set to detect hallucinations.

---

## [12] Governance: Prompt hacking guardrails (+1)
* **Status:** Done
### Actions & Description:
System Prompt Isolation: Hardcode strict system rules that block commands containing malicious text patterns (like "ignore previous instructions").

---

## [13] Governance: Info exfiltration blockers (+2)
* **Status:** Done
### Actions & Description:
Mask PII: Add a scanning step that detects regex patterns for credit card numbers, social security digits, or emails.

Anonymize Outputs: Redact or replace private data with asterisks (***) before sending text out to public cloud models.

---

## [18] Scaling: Redis background message queue (+3)
* **Status:** Done
### Actions & Description:
Simulate Multi-User Traffic: Create an array list that stacks incoming client simulation jobs in a strict numerical sequence.

Process Worker Loop: Run through the list one-by-one to protect server resources from spiking during high-traffic waves.

---

## [10] Agentic: Session-persistent context memory (+2)
* **Status:** Done
### Actions & Description:
Capture Session Signature: Generate a unique session token identifier using Python's uuid module whenever a client logs into the interface.

Disk Cache Synchronization: Write an automated storage step that dumps st.session_state.messages to a localized JSON file (history_session.json) on every message turn, allowing complete conversation recovery if the web server restarts or crashes.

---

## [8] Agentic: Self-correcting reflection loop (+2)
* **Status:** Done
### Actions & Description:
Self-Review Step: Pass the agent's draft response to a critic function to look for missing details or hallucinations.

Fallback Rerouting: If confidence score drops below 80%, trigger a rewrite or fall back to a safe default template.

---

## [9] Agentic: Performance improvement user feedback loop (+3)
* **Status:** Done
### Actions & Description:
Add Thumbs Up/Down: Place interactive rating buttons underneath the chat bubbles in Streamlit.

Log Responses: Save poorly rated responses to an internal text log file so you can show the panel how you collect bad data for future tuning.

---

## [16] Scaling: Semantic routing layer (Flash vs Pro) (+3)
* **Status:** Done
### Actions & Description:
Evaluate Complexity: Inspect incoming queries for length and depth (e.g., "Hi" vs. "Rebalance my tax assets").

Model Routing Switch: Route basic chat greetings to a light, cheap model, and pass complex questions to a premium model.

---

## [22] RAG: Ingest 10+ docs with keyword search (1000 chunks)
* **Status:** Done
### Actions & Description:
Text Document Chunking: Write a script to slice 10 dummy text files into exactly 1,000 small, searchable fragments.

Keyword Matrix Indexing: Build a basic keyword scanning index (like a Python search dictionary) to match user words directly to exact text files.

---

## [17] Scaling: Redis performance cache with TTL (+2)
* **Status:** Done
### Actions & Description:
Build Memory Cache Map: Create a local lookup table to save past answers to repetitive questions (e.g., "What is inflation today?").

Time-To-Live (TTL): Set an expiration countdown so saved answers wipe automatically after 60 seconds to ensure data stays fresh.

---

## [4] RAG: Hybrid search workflow (Vector + Keyword) (+2)
* **Status:** Done
### Actions & Description:
Merge Core Results: Combine the outputs of the semantic search and the keyword search into a unified list.

Deduplicate Entries: Clean the list so that if a document fragment appears in both search types, it is only shown once.

---

## [19] Core: Basic chat interface as a web app (+2)
* **Status:** Done
### Actions & Description:
Task 1: Streamlit Chat UI Wiring (Allocated: 1.0 Hour)Deliverable: Refactor the current form layout in app/frontend.py into a modern chat stream using native widgets: st.chat_input() to capture questions and st.chat_message("user") / st.chat_message("assistant") to display the conversation log.

Task 2: Session State management for chat history persistence (Allocated: 0.5 Hours)Deliverable: Initialize and update st.session_state.messages. Without this, Streamlit will completely wipe your entire chat history every single time you click a button or type a new message.

Task 3: Connect Frontend Chat to Async Backend Streams (Allocated: 0.5 Hours)Deliverable: Update httpx.AsyncClient in the frontend to call your chat endpoint and unpack the response text fluidly, verifying that errors are caught gracefully if the backend takes too long to respond.

---

## [3] RAG: Metadata-enhanced semantic search (+2)
* **Status:** Done
### Actions & Description:
Tag Chunks: Add metadata tags (e.g., category: "tax_planning", client_tier: "premium") to your text fragments.

Filtered Searching: Write a query filter that matches chunks based on meaning, restricted to matching metadata tags.

---

## [14] Governance: Human-in-the-loop exception handling (+4)
* **Status:** Done
### Actions & Description:
Interception Gate: If the agent suggests a portfolio change, flag it as PENDING_REVIEW on the backend.

Interactive Review UI: Build an advisor review layout in Streamlit with an "Approve" button, a "Reject" button, and a st.text_input("Provide correction notes...") field.

Feedback Integration: If rejected, append the correction notes to a local file (feedback_logs.json) so the agent can read past corrections and automatically improve its next response.

---

## [5] RAG: Custom recency-weighted reranker (+2)
* **Status:** Done
### Actions & Description:
Apply Timestamps: Assign dates to every document fragment in your database.

Rerank Scoring: Boost the priority score of newer articles so the AI always prefers fresh market data over outdated data.

---

## [1] Core: 3-Agent sequential workflow (+2)
* **Status:** Done
### Actions & Description:
Define Roles: Outline explicit instructions for an InTake Agent, a Risk Analyst Agent, and a Portfolio Reviewer Agent.

Sequential Hand-off: Build a bridge where Agent 1's text output passes cleanly as the input to Agent 2, then Agent 3.

---

## [20] Core: Current system design diagram (+2)
* **Status:** Done
### Actions & Description:
Map Code Pathways: Document the actual flow of data from Streamlit to FastAPI and the Agent chains.

Render Architecture Visual: Use a tool (like Mermaid or a markdown graphic) to embed a clear, high-level map directly into your project's README.md file.

---

## [21] Advanced: Async/Event-driven backend infrastructure (+2)
* **Status:** Done
### Actions & Description:
Task 1: Build async FastAPI event loop structure (Allocated: 1.0 Hour) (Done today!)Deliverable: Configured app/main.py with non-blocking async endpoint handlers (async def) and simulated heavy calculations using asyncio.sleep.

Task 2: Build an asynchronous background task queue (Allocated: 0.5 Hours)Deliverable: Integrate FastAPI's native BackgroundTasks or an in-memory queue. This allows the API to immediately return a tracking ID to the frontend while a simulation calculates heavily in the background without locking up the server thread.

Task 3: Create an async mock-streaming data generator (Allocated: 0.5 Hours)Deliverable: Build a generator function using async for that streams simulated asset pricing ticks chunk-by-chunk rather than returning a single massive JSON block at the end.

---

## [2] Advanced: Multi-turn dialogue state management (+2)
* **Status:** Done
### Actions & Description:
Design Payload State: Structure a JSON format to track whether the user is talking about onboarding, rebalancing, or risk assessment.

Context Switching: Write logic that shifts the backend's focus dynamically when a user changes the topic mid-chat.

---

## [7] Agentic: Hierarchical orchestrator agent (+2)
* **Status:** Done
### Actions & Description:
Scaffold Manager Role: Create a central Orchestrator Agent that listens to the user's question and decides which specialist agent to route it to.

Delegate & Consolidate: Route tasks outward and collect the sub-agent answers into a single, comprehensive final message.

---

## [15] Governance: Workflow reasoning explainability logs (+2)
* **Status:** Done
### Actions & Description:
Build "Thought Process" Log: Track the exact steps the AI took (e.g., Step 1: Read files -> Step 2: Searched risk profile -> Step 3: Drafted summary).

Accordion UI Container: Render this breakdown inside a clean, collapsible st.expander("Show Reasoning Path") block in the chat 

Trace Payload Compilation: Update the 3-agent dictionary to track processing timestamps and key data variables extracted at each internal node step.

Deploy Accordion UI: Render this execution map inside a native, collapsible st.expander("🔍 Show Multi-Agent Operational Trace Logs") directly above the advisor form block.interface.

---

## [23] Infrastructure: Local Pyenv Environment Compilation & Core Workspace Activation (+0)
* **Status:** Done
### Actions & Description:


---

## [24]  Infrastructure: Initialize repo, scaffold core app files, and fix Git authentication
* **Status:** Done
### Actions & Description:


---

## [25] Infrastructure: Initialize kayawealth-core project board and rebalance 4-day sprint roadmap
* **Status:** Done
### Actions & Description:


---

## [26] Infrastructure: Core Codebase Refactor & Structural Modularisation
* **Status:** Done
### Actions & Description:
Decouple Search Matrix: Extract pure filtering logic out of app/main.py into a separate helper module (app/services/search.py).

Enforce Pydantic Enums: Replace loose status string literals ("pending", "processing") with a strict Pydantic class object to maintain consistent system state representation.

---

## [27] Infrastructure: Content Testing
* **Status:** Done
### Actions & Description:
User Feedback:

- I dont understand anything and the purpose for this web page 
- It has no customer friendly vibes its cold boring and makes no sense as to what its purpose is 
- It is not working it keeps repeating itself with the same statement about noting stuff 
- How will we move forward if its only taking notes and unable to provide recommendations or ask financially literate questions to get the conversation moving

Role 1: The Client (Testing the Chat Interface)Action: Go to the chat bar and type: "Run agent simulation for my retirement account."Goal: Verify the system halts with a yellow warning (PENDING_REVIEW) and doesn't leak the raw report instantly to the client.

Role 2: The Wealth Advisor (Testing Data & Governance Control)Action: Review the internal logs in the expander dropdown. Type a correction note in the input box (e.g., "Reduce international equity exposure by 5%."), then click Reject & Log Correction.Goal: Ensure the critique is saved to the conversation log.

Role 3: The Compliance Auditor (Testing Knowledge Accuracy)Action: Go to the left sidebar. Type "tax" or "compliance" into the Hybrid Search box. Change the filters from 2024 to 2026.Goal: Verify that fresh 2026 files score a high 1.5 rating and appear at the top.

---

## [28] Infrastructure: Environment Infrastructure Configuration (Dev/Test/Prod Pipeline)
* **Status:** In Progress
### Actions & Description:
Externalize Settings: Create a localized .env configuration file to store active parameters outside your application logic.

Build Config Loader: Inject a native Python config dictionary handler into app/main.py that reads the active track (DEV, TEST, or PROD) and scales cache TTL thresholds dynamically.


---

## [29] Multi-Agent Orchestration & Contextual Intent Routing Matrix
* **Status:** Done
### Actions & Description:
Intent Arbiter Node: Construct a central LLM coordinator node that reads incoming user inputs and dynamically branches execution paths between the RAG search service, the persistent feedback loop, and the 3-agent core.

Conflict Resolution Engine: Build a scoring loop that checks advisor corrections in feedback_logs.json against client queries, ensuring conflicting constraints (e.g., a client asking for high-risk assets vs. an advisor's low-volatility mandate) are flagged before a report compiles.

---

## [30] Check Functionality Against Brief
* **Status:** Todo
### Actions & Description:
    • AuraWealth is a consumer facing wealth management that bridges the gap between high-touch human advice and digital efficiency. It replaces fragmented spreadsheets and manual reporting with a unified, transparent platform for both everyday investors and their wealth managers.
      
    • [Client] For the client, the app serves as a "financial GPS," offering a real-time, holistic view of their entire net worth alongside visual progress tracking for specific life goals. It removes the friction of traditional banking through a secure concierge and instant AI advisor access via an in app chat interface.
      
    • [Advisor] For the advisor, the backend portal acts as a "command center" designed to scale personal service. By automating administrative burdens like client portfolio review, risks analysis, managing conversation with clients and portfolio rebalancing, and using AI-driven insights to flag clients in need of attention, advisors can manage a larger book of business while deepening individual relationships. Ultimately, AuraWealth transforms wealth management from a series of static reports into a collaborative, real-time partnership.

---

## [31] Core: Async Frontend Chat Transport Remediation
* **Status:** Todo
* **Effort:** 1.5–2.5 hrs
* **Complexity:** Medium
### Actions & Description:
Replace the synchronous `httpx.post()` call in the main Streamlit chat path with an `httpx.AsyncClient` request executed safely from the frontend runtime.

Preserve timeout and error handling behaviour, then verify in the UI that normal advisory responses and blocked requests both render correctly without freezing the chat interface.

---

## [32] Advanced: Async Mock Market-Tick Streaming Generator
* **Status:** Todo
* **Effort:** 2–3 hrs
* **Complexity:** Medium
### Actions & Description:
Create an async generator that yields simulated asset-price ticks incrementally instead of returning one complete payload.

Expose the generator through an async FastAPI streaming endpoint and add a frontend demonstration panel that visibly receives several ticks over time.

---

## [33] RAG: Semantic Retrieval Architecture Decision & Remediation
* **Status:** Todo
* **Effort:** 2–5 hrs
* **Complexity:** High
### Actions & Description:
Document the current retrieval implementation accurately as lexical title/keyword matching and record the cost, latency, privacy, and operational trade-off of adding embeddings.

Choose one implementation path: retain lexical retrieval with corrected documentation, or add a local embedding model/vector index and use it in the existing hybrid-search workflow. Demonstrate the selected path in the UI and README.

---

## [34] Governance: Persisted PENDING_REVIEW Recommendation State
* **Status:** Done
* **Effort:** 2–3.5 hrs
* **Complexity:** Medium
### Actions & Description:
Create a backend recommendation state model that automatically assigns `PENDING_REVIEW` whenever a workflow produces a portfolio-change recommendation.

Persist the status with the recommendation record, prevent direct client delivery until an advisor approval action is recorded, and verify approval/rejection behaviour through the advisor UI.

---

## [35] Scaling: Semantic Router Integration Audit
* **Status:** Todo
* **Effort:** 1–2 hrs
* **Complexity:** Low
### Actions & Description:
Trace the live Streamlit chat path through the #29 intent orchestrator and determine whether the #16 Flash/Pro routing decision is applied before agent execution.

Either integrate the model-tier router into the production chat path with visible route telemetry, or document why #29 supersedes it and update the architecture diagram accordingly.

---

## [36] Documentation: Code-Accurate Architecture and Capability Claims
* **Status:** Done
* **Effort:** 1.5–2.5 hrs
* **Complexity:** Medium
### Actions & Description:
Reconcile `README.md` with the codebase. Remove or clearly label as future-state any claims of LangGraph, Qdrant/Chroma, live Gemini API integration, or other components not implemented locally.

Update the Mermaid diagram, technology stack, walkthrough, and panel-defense matrix to distinguish implemented components, simulations, and planned production integrations.

---

## [37] Governance: Feedback-Driven Quality Improvement Benchmark
* **Status:** Todo
* **Effort:** 2.5–4 hrs
* **Complexity:** High
### Actions & Description:
Extend #9 and #11 with a repeatable before/after benchmark that uses simulated advisor critique records to evaluate whether feedback-aware responses score higher than baseline responses.

Record the evaluation inputs, scores, pass criteria, and observed improvement in a frontend-visible result so the panel can verify the feedback loop objectively.

---

## [38] Infrastructure: Board Status and Evidence Reconciliation
* **Status:** Done
* **Effort:** 0.5–1 hr
* **Complexity:** Low
### Actions & Description:
Review completion evidence and Git commits for #7, #11, #12, and #13. Update their `TASKS.md` status fields and GitHub Project status to match verified implementation and frontend test results.

Add the implementing commit SHA to each completed task description or linked project note so the panel can trace feature evidence quickly.

---

## [39] Infrastructure: Test-Driven Development Quality Gate
* **Status:** Done
* **Effort:** 3–5 hrs
* **Complexity:** High
### Actions & Description:
Establish a `pytest` test suite with isolated fixtures for session files, feedback logs, Redis, and FastAPI routes. Add focused unit tests for the security guardrails, PII redaction, retrieval/reranking, dialogue state, evaluator, Redis cache, Redis queue, and orchestration conflict controls.

Add frontend smoke tests for the Streamlit chat, evaluation, cluster map, queue, and operational trace panels. Require new feature work and the #26 refactor to begin with a failing test where practical, then pass the full suite before each atomic commit.

---

## [40] Client Experience: Financial GPS Net-Worth and Goal Progress View
* **Status:** Todo
* **Effort:** 3–5 hrs
* **Complexity:** Medium
### Actions & Description:
Add a simulated client dashboard that displays a consolidated net-worth snapshot, asset allocation summary, and visual progress toward at least two life goals.

Keep all values explicitly labelled as demo data, make the view separate from advisor-only controls, and verify that the client experience supports the Financial GPS description in the assessment brief.

---

## [42] Architecture: Non-Functional Requirements Baseline
* **Status:** Todo
* **Effort:** 3–4.5 hrs
* **Complexity:** Medium
### Actions & Description:
Define measurable non-functional requirements for the prototype and its production target. Cover performance and latency, availability and failure behaviour, horizontal scalability, security and data governance, observability, accessibility, resilience/recovery, FinOps cost controls, and operational support.

Document a clear distinction between the local demonstration baseline and the target production architecture. For each requirement, record a measurable acceptance criterion, an owner/component, the current implementation status, and a verification method.

Add lightweight reproducible checks where feasible: API health and dependency-failure handling, cache/queue fallback behaviour, response-time sampling for core routes, and the existing automated test suite. Record known gaps and their production remediation path without claiming guarantees the local prototype cannot prove.

---
