# KayaWealth: Core Enterprise Infrastructure Prototype

KayaWealth is an asynchronous, event-driven, agentic-first consumer wealth management engine tailored for regional high-net-worth ecosystems. It bridges the gap between high-touch human advice and digital efficiency by automating client portfolio reviews, risk analysis, and client-advisor communication workflows.

This repository contains the core architectural skeleton, advanced RAG infrastructure, and security guardrails built during a 5-day unsupervised technical assessment.

## 🏗️ Core Architecture Overview
- **Orchestration Framework:** LangGraph (State Graph Engine)
- **Backend Infrastructure:** FastAPI (Fully Asynchronous Event Loop)
- **Vector Engine:** Qdrant / ChromaDB (Hybrid Vector & Keyword Search)
- **Event & Performance Layer:** Redis (Async Caching, Session Memory, Message Queue)
- **Strategic AI Safety:** Dual-layer guardrails (Prompt Injection & Exfiltration Defense) + Automated Evaluators

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Redis Server
- API Keys: Gemini Enterprise / Cursor Environment Config

### Installation & Setup
```bash
# Clone the repository
git clone <your-repo-url> kayawealth-core
cd kayawealth-core

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload

# Run the frontend portal
streamlit run app/frontend.py
```

## 📊 System Design Diagram
```mermaid
graph TD
    %% Client & Interface Layer
    User[📱 Client/Advisor UI: Streamlit] -->|1. Async HTTP Request| API[⚡ API Gateway: FastAPI]
    
    %% Core Backend Orchestration
    subgraph Core Backend Engine (Asyncio Loop)
        API -->|2. Multi-turn Session State| StateManager[🧠 Context Dialogue State Manager]
        StateManager -->|3. Route Query| Router{🤖 Semantic Model Router}
    end

    %% Model Routing Logic
    Router -->|Simple Query: Low Latency| FlashModel[Gemini Flash / Small LLM]
    Router -->|Complex Task: Multi-Agent| Orchestrator[👑 LangGraph Hierarchical Orchestrator]

    %% Multi-Agent Processing Framework
    subgraph Agentic Reasoning Cluster (LangGraph State Machine)
        Orchestrator --> Agent1[📋 Portfolio Ingestion Agent]
        Orchestrator --> Agent2[⚖️ Risk Analysis Agent]
        Orchestrator --> Agent3[✍️ Executive Reporting Agent]
        Agent2 --> Reflection{🔍 Self-Correction Critic}
        Reflection -->|Fail: Confidence Score Low| Agent2
    end

    %% External Infrastructure & Security
    subgraph Data & Optimization Layer
        FlashModel & Agent3 -->|4. Structural Output| Guardrails[🛡️ Security Guardrails: Injection & Exfiltration Filters]
        Guardrails -->|5. Verify Data Boundaries| API
        Agent2 -.->|Read/Write Cache| RedisCache[(🚀 Redis Performance Cache & MQ)]
    end
```
