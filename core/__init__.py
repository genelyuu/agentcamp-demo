"""
core - AgentCamp Business Logic Layer
ADR-101: UI/Core Boundary Separation
ADR-106: Citation Transparency
ADR-108: Explainable Routing
ADR-109: Structured Rubric Scoring
ADR-110: Offline-first + LLM-enhanced 아키텍처
LOG-002, ERR-001: Logging & Error Handling
"""
from .api import AgentCampAPI
from .orchestrator import (
    route_agent,
    route_agent_with_reason,
    answer_with_twin,
    answer_with_citations,
    route_and_answer,
    generate_answer,  # ADR-110: Offline-first + LLM-enhanced
    set_llm_client,
    get_llm_client,
    ROUTING_LEXICON,
)
from .evaluation import simple_review, review_with_task, review_with_evidence, rubric_review
from .citation import (
    find_relevant_knowledge,
    extract_keyword_context,
    pick_citations,
    get_active_knowledge_top3,
)
from .twin_renderer import (
    StructuredSection,
    StructuredAnswer,
    render_twin_answer,
    render_ceo_answer,
    render_pm_answer,
    render_frontend_answer,
    render_backend_answer,
    get_available_renderers,
)
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
from .logger import (
    logger,
    get_logger,
    setup_logger,
    log_request,
    log_response,
    log_llm_call,
    log_error,
    log_security_event,
    log_audit,
)
from .errors import (
    init_sentry,
    capture_exception,
    AgentCampError,
    ValidationError,
    LLMError,
    SecurityError,
    StorageError,
    create_error_response,
    handle_errors,
    safe_execute,
)

__all__ = [
    # Facade API
    "AgentCampAPI",
    # Orchestrator
    "route_agent",
    "route_agent_with_reason",
    "answer_with_twin",
    "answer_with_citations",
    "route_and_answer",
    "generate_answer",  # ADR-110: Offline-first + LLM-enhanced
    "set_llm_client",
    "get_llm_client",
    "ROUTING_LEXICON",
    # Evaluation
    "simple_review",
    "review_with_task",
    "review_with_evidence",
    "rubric_review",
    # Citation (ADR-106)
    "find_relevant_knowledge",
    "extract_keyword_context",
    "pick_citations",
    "get_active_knowledge_top3",
    # Twin Renderer (ADR-108)
    "StructuredSection",
    "StructuredAnswer",
    "render_twin_answer",
    "render_ceo_answer",
    "render_pm_answer",
    "render_frontend_answer",
    "render_backend_answer",
    "get_available_renderers",
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
    # Logging (LOG-002)
    "logger",
    "get_logger",
    "setup_logger",
    "log_request",
    "log_response",
    "log_llm_call",
    "log_error",
    "log_security_event",
    "log_audit",
    # Errors (ERR-001)
    "init_sentry",
    "capture_exception",
    "AgentCampError",
    "ValidationError",
    "LLMError",
    "SecurityError",
    "StorageError",
    "create_error_response",
    "handle_errors",
    "safe_execute",
]
