# AgentCamp - AI-Powered OJT Digital Twins Platform

> **Version 1.0** | AI System Architecture Document

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agentcamp-demo-kvnmnjquyv6jfmwqhjt4f4.streamlit.app/)

---

## 1. Executive Summary

| Item | Description |
|------|-------------|
| **Project Name** | AgentCamp |
| **Version** | 1.0 |
| **Type** | AI-Powered OJT (On-the-Job Training) Platform |
| **Core Concept** | 4 Digital Twin Agents for New Hire Mentoring |
| **Team** | Veluga |
| **License** | MIT |

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AgentCamp v1.0                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Presentation Layer                            │   │
│  │                     (app.py - Streamlit)                         │   │
│  │         [Admin Mode] [New Hire Mode] [Dashboard Mode]            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Business Logic Layer                          │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │   │
│  │  │ orchestrator │ │   scoring    │ │  ingestion   │             │   │
│  │  │  (Routing)   │ │ (Evaluation) │ │ (Extraction) │             │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Integration Layer                             │   │
│  │  ┌──────────────┐ ┌──────────────────────────────────────────┐  │   │
│  │  │    agents    │ │              llm_client                   │  │   │
│  │  │  (4 Twins)   │ │    [Mock] [Claude API] [OpenAI API]       │  │   │
│  │  └──────────────┘ └──────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Layer (storage.py)                       │   │
│  │            [org.json] [knowledge.json] [sessions.json]           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Responsibilities (SOLID Principles)

| Module | Responsibility | Design Pattern |
|--------|---------------|----------------|
| `app.py` | Streamlit UI (Admin/NewHire/Dashboard) | MVC - View |
| `agents.py` | Digital Twin persona definitions | Data Class |
| `orchestrator.py` | Question routing + response generation | Strategy Pattern |
| `llm_client.py` | LLM abstraction (Mock/Claude/OpenAI) | Factory + Abstract Base |
| `storage.py` | JSON-based persistence | Repository Pattern |
| `ingestion.py` | Text extraction from STT/Slack | ETL Pipeline |
| `scoring.py` | Rubric-based submission evaluation | Scoring Engine |

---

## 4. Digital Twin Agents

| Agent | Role | Keywords (Routing) | Communication Style |
|-------|------|-------------------|---------------------|
| **Sam Lee** | CEO | 우선순위, 전략, 고객, 리스크, 비용 | 짧고 결론 중심. 비용/속도/리스크를 함께 본다 |
| **JH Kim** | PM | 요구사항, 스코프, 정의, KPI, 지표 | 요구사항을 명확히 쪼개고 성공조건으로 정리 |
| **Seul Kim** | Frontend | UI, UX, 화면, 프론트, component | 사용자 흐름, UX, 에러 케이스, 구현 난이도 동시 고려 |
| **Jin Park** | Backend | Default (fallback) | 시스템 관점. 데이터/성능/안정성/배포 기준 판단 |

---

## 5. Data Flow Architecture

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│  User Input  │───▶│  orchestrator   │───▶│  route_agent │
└──────────────┘    │   .route()      │    │   (keyword)  │
                    └─────────────────┘    └──────┬───────┘
                                                  │
                    ┌─────────────────┐           ▼
                    │   TwinAgent     │◀──────────┘
                    │   (Selected)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐    ┌──────────────┐
                    │  answer_with_   │───▶│  llm_client  │
                    │     twin()      │    │  .generate() │
                    └────────┬────────┘    └──────────────┘
                             │
                    ┌────────▼────────┐    ┌──────────────┐
                    │    Response     │───▶│   storage    │
                    │                 │    │  .set_*()    │
                    └─────────────────┘    └──────────────┘
```

---

## 6. Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Streamlit | >= 1.37.0 |
| **Data Validation** | Pydantic | >= 2.8.0 |
| **Environment** | python-dotenv | >= 1.0.0 |
| **LLM - Claude** | anthropic | >= 0.18.0 |
| **LLM - OpenAI** | openai | >= 1.0.0 |
| **Data Storage** | JSON (Demo) / Supabase (Production) | - |
| **Deployment** | Streamlit Cloud | - |

---

## 7. LLM Integration Architecture

| Provider | Model | Use Case |
|----------|-------|----------|
| **Mock** | - | Demo/Testing (No API key required) |
| **Claude** | claude-sonnet-4-20250514 | Production (Anthropic API) |
| **OpenAI** | gpt-4o | Alternative (OpenAI API) |

---

## 8. Project Structure

```
agentcamp-demo/
├── app.py                 # Streamlit UI (Admin/NewHire/Dashboard)
├── agents.py              # 4 Digital Twin definitions
├── orchestrator.py        # Question routing + response generation
├── llm_client.py          # LLM client abstraction (Mock/Claude/OpenAI)
├── storage.py             # JSON persistence layer
├── ingestion.py           # Text extraction pipeline
├── scoring.py             # Rubric-based evaluation
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
├── .streamlit/
│   └── config.toml        # Streamlit configuration
└── data/
    ├── org.json           # Organization settings + rubric
    ├── knowledge.json     # Extracted knowledge items
    ├── sessions.json      # User session data
    └── demo_inputs/       # Sample STT/Slack files
```

---

## 9. Quick Start

```bash
# 1. Clone repository
git clone https://github.com/genelyuu/agentcamp-demo.git
cd agentcamp-demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
streamlit run app.py
```

### LLM Configuration (Optional)

| Step | Action |
|------|--------|
| 1 | Select **LLM Provider** in Sidebar: `mock` / `claude` / `openai` |
| 2 | Enter **API Key** (not required for mock mode) |
| 3 | Select **Model** |
| 4 | Click **"LLM 적용"** button |

---

## 10. Key Features

| Mode | Feature | Description |
|------|---------|-------------|
| **Admin** | Knowledge Ingestion | Upload STT/Slack exports for knowledge extraction |
| **Admin** | Rubric Setup | Define evaluation keywords (완료/지표/정의/우선순위) |
| **New Hire** | OJT Questions | Ask questions to 4 Digital Twin mentors |
| **New Hire** | Task Submission | Submit work for AI-powered feedback |
| **Dashboard** | Analytics | View adaptation/risk scores per user |
| **Dashboard** | Session History | Track question history and responses |

---

## 11. Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each module has one clear purpose |
| **Open/Closed** | LLM providers extensible via BaseLLMClient |
| **Liskov Substitution** | All LLM clients interchangeable |
| **Interface Segregation** | Minimal abstract methods in BaseLLMClient |
| **Dependency Inversion** | orchestrator depends on abstraction, not concrete LLM |

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | 2026-01-19 | Initial release with 4 Digital Twins, Mock/Claude/OpenAI support |

---

## 13. Roadmap

| Status | Feature |
|--------|---------|
| ✅ | MVP Demo (Current) |
| ⬜ | Supabase Integration (Persistent storage) |
| ⬜ | Voice Input (Real-time STT) |
| ⬜ | Multi-turn Conversation Memory |
| ⬜ | Slack/Teams Integration |
| ⬜ | API Layer (B2B SaaS) |

---

## 14. Team

**Veluga** - AI-Powered Onboarding Solutions

---

## 15. License

MIT License

---

<p align="center">
    <b>Built with AI System Architecture principles for scalable OJT mentoring.</b><br>
    <i>Version 1.0 | Principal Architect Documentation</i>
</p>
