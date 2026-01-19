"""
core - AgentCamp Business Logic Layer
ADR-101: UI/Core Boundary Separation
"""
from .api import AgentCampAPI
from .orchestrator import route_agent, answer_with_twin, set_llm_client, get_llm_client
from .evaluation import simple_review, review_with_task
from .storage import (
    get_org,
    set_org,
    get_knowledge,
    set_knowledge,
    get_sessions,
    set_sessions,
)
from . import risk
from . import incident

__all__ = [
    # Facade API
    "AgentCampAPI",
    # Orchestrator
    "route_agent",
    "answer_with_twin",
    "set_llm_client",
    "get_llm_client",
    # Evaluation
    "simple_review",
    "review_with_task",
    # Storage
    "get_org",
    "set_org",
    "get_knowledge",
    "set_knowledge",
    "get_sessions",
    "set_sessions",
    # Risk (ADR-105)
    "risk",
    "incident",
]
