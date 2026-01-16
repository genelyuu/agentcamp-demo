# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentCamp Demo is an AI-powered OJT (On-the-Job Training) platform with 4 Digital Twin agents. It supports Mock mode (no LLM API key required) and can upgrade to Claude/OpenAI when keys are available.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

# Optional: Install LLM packages
pip install anthropic  # For Claude
pip install openai     # For OpenAI
```

## Architecture

### Design Principles
- **SOLID**: Single responsibility per module, dependency injection for LLM clients
- **Separation of Concerns**: UI (app.py) → Business Logic (orchestrator, scoring) → Data (storage)

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `storage.py` | JSON-based persistence (org, knowledge, sessions) |
| `agents.py` | Digital Twin definitions (4 personas with styles/rules) |
| `orchestrator.py` | Question routing + response generation |
| `ingestion.py` | Text extraction → knowledge items |
| `scoring.py` | Rubric-based submission evaluation |
| `app.py` | Streamlit UI (Admin/NewHire/Dashboard modes) |

### Data Flow
```
User Input → app.py → orchestrator.route_agent() → TwinAgent
                   → orchestrator.answer_with_twin() → Response
                   → scoring.simple_review() → Feedback
                   → storage.set_*() → JSON files
```

### Digital Twin Routing
- **Sam Lee (CEO)**: 우선순위, 전략, 고객, 리스크, 비용
- **JH Kim (PM)**: 요구사항, 스코프, 정의, kpi, 지표
- **Seul Kim (Frontend)**: ui, ux, 화면, 프론트, component
- **Jin Park (Backend)**: Default fallback

### Data Files (auto-created in `data/`)
- `org.json`: Organization settings + rubric keywords
- `knowledge.json`: Extracted knowledge items from STT/Slack
- `sessions.json`: User sessions with adapt/risk scores

## Extension Points

To add real LLM support, modify `answer_with_twin()` in `orchestrator.py`:
```python
# Replace mock template with actual API call
client = anthropic.Anthropic()
response = client.messages.create(...)
```
