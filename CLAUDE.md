# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**AgentCamp** - AI-powered OJT (On-the-Job Training) platform with 4 Digital Twin mentors.
- **Status**: Hackathon (v1.0 Demo → v1.2 Production-Ready)
- **Team**: Veluga
- **Principles**: SOLID, Separation of Concerns, Clean Architecture

## Commands

```bash
# Install
pip install -r requirements.txt

# Run
streamlit run app.py              # http://localhost:8501

# Test (v1.2)
pytest tests/                     # All tests
pytest tests/eval_suite/          # Evaluation Gate only
pytest tests/unit/ -v             # Unit tests verbose

# Deploy
git push origin main              # Streamlit Cloud auto-deploys
```

## Architecture (v1.0 → v1.2)

### Current Structure (v1.0)
```
app.py (UI + Logic mixed)
├── orchestrator.py  → Question routing + LLM delegation
├── llm_client.py    → Mock/Claude/OpenAI factory pattern
├── agents.py        → 4 TwinAgent dataclasses
├── storage.py       → JSON persistence (data/*.json)
├── ingestion.py     → STT/Slack text extraction
└── scoring.py       → Rubric-based evaluation
```

### Target Structure (v1.2 - ADR-101)
```
app.py (UI only - Thin Layer)
└── core/
    ├── api.py           → Boundary contract (AgentCampAPI)
    ├── orchestrator.py  → Business logic
    ├── evaluation.py    → Scoring engine
    ├── storage.py       → Repository pattern
    └── llm/             → Capability-based LLM (ADR-104)
        ├── router.py    → RouterCapability
        ├── answerer.py  → AnswererCapability
        └── judge.py     → JudgeCapability
schemas/                 → Pydantic models (ADR-102)
tests/eval_suite/        → Golden set tests (ADR-103)
```

### Digital Twin Routing (`orchestrator.py:11-15`)

| Twin | Role | Keywords | Fallback |
|------|------|----------|----------|
| Sam Lee | CEO | 우선순위, 전략, 고객, 리스크, 비용 | - |
| JH Kim | PM | 요구사항, 스코프, 정의, kpi, 지표 | - |
| Seul Kim | Frontend | ui, ux, 화면, 프론트, component | - |
| Jin Park | Backend | * | Default |

### LLM Client Factory (`llm_client.py:182-215`)

```python
from llm_client import create_llm_client

client = create_llm_client("mock")                            # No API key
client = create_llm_client("claude", api_key, "claude-sonnet-4-20250514")
client = create_llm_client("openai", api_key, "gpt-4o")
```

## Design Principles (SOLID)

| Principle | Current Implementation |
|-----------|----------------------|
| **S**ingle Responsibility | Each module has one purpose |
| **O**pen/Closed | `BaseLLMClient` extensible for new providers |
| **L**iskov Substitution | All LLM clients interchangeable |
| **I**nterface Segregation | Minimal `generate_response()` contract |
| **D**ependency Inversion | orchestrator depends on abstraction |

## Extension Points

**Add LLM provider:**
1. Extend `BaseLLMClient` in `llm_client.py`
2. Implement `generate_response(twin, org, knowledge, question)`
3. Add case to `create_llm_client()` factory

**Add Digital Twin:**
1. Add `TwinAgent` in `agents.py:get_twins()`
2. Add keywords to `_ROUTING_RULES` in `orchestrator.py`

**Add Pydantic schema (v1.2):**
1. Create model in `schemas/`
2. Apply validation in `storage.py` save/load

## Data Files (auto-created in `data/`)

| File | Purpose |
|------|---------|
| `org.json` | Organization config + rubric keywords |
| `knowledge.json` | Extracted knowledge items with source tags |
| `sessions.json` | User sessions with adapt/risk scores |

## Configuration

**Streamlit secrets** (`.streamlit/secrets.toml` - gitignored):
```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
```

## ADR Reference (docs/adr/)

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-101 | UI/Core Boundary Separation | v1.2 |
| ADR-102 | Pydantic Data Contracts | v1.2 |
| ADR-103 | Evaluation Gate (Golden Set) | v1.2 |
| ADR-104 | LLM Capability Interface | v1.2 |
| ADR-105 | Risk Register | v1.2 |

## Task Backlog

See `docs/TASK_BACKLOG.md` for 78 tickets across 9 sprints targeting v1.2.

## Critical Path (Hackathon Focus)

```
Phase 1: Foundation
├── ARCH-001~008 (UI/Core Boundary)
├── SCHEMA-001~008 (Data Contract)
└── CAP-001~010 (LLM Capability)

Phase 2: Quality Gates
├── EVAL-001~008 (Golden Set Tests)
└── TEST-001~008 (Unit Tests)
```

## Quick Reference

| 작업 | 파일 위치 |
|------|----------|
| Twin 응답 스타일 수정 | `agents.py` → `TwinAgent.style` |
| 라우팅 키워드 추가 | `orchestrator.py:11-15` → `_ROUTING_RULES` |
| 평가 로직 변경 | `scoring.py` → `simple_review()` |
| LLM 프롬프트 수정 | `llm_client.py` → `_build_system_prompt()` |
| UI 모드 추가 | `app.py` → `MODE_OPTIONS` |

## Documentation

| 문서 | 대상 |
|------|------|
| `docs/EXECUTIVE_REPORT.md` | C-Level 보고 |
| `docs/VERSION_COMPARISON.md` | v1.0 vs v1.2 비교 |
| `docs/diagrams/` | Mermaid 아키텍처 다이어그램 |
| `docs/images/` | 렌더링된 PNG 이미지 |
