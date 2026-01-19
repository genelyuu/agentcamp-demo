"""
schemas - Pydantic Data Contracts
ADR-102: Data Contract with Pydantic Schemas
ADR-108: Explainable Routing
ADR-109: Structured Rubric Scoring
"""
from .enums import (
    KnowledgeTag,
    KnowledgeSource,
    RiskCategory,
    Severity,
    IncidentStatus,
)
from .knowledge import KnowledgeItem, KnowledgeBase
from .organization import OrgConfig, RubricConfig
from .session import UserSession, SessionStore, OJTTask, ChatMessage
from .audit import AuditEvent
from .risk import RiskEntry, Incident, RiskRegister, IncidentLog
from .response import Citation, AnswerResult, KeywordMatch, ReviewResult
from .routing import Candidate, RoutingResult
from .rubric import (
    ChecklistItem,
    RubricColumn,
    RubricReviewResult,
    calculate_grade,
    create_empty_rubric_result,
)

__all__ = [
    # Enums
    "KnowledgeTag",
    "KnowledgeSource",
    "RiskCategory",
    "Severity",
    "IncidentStatus",
    # Knowledge
    "KnowledgeItem",
    "KnowledgeBase",
    # Organization
    "OrgConfig",
    "RubricConfig",
    # Session
    "UserSession",
    "SessionStore",
    "OJTTask",
    "ChatMessage",
    # Audit
    "AuditEvent",
    # Risk (ADR-105)
    "RiskEntry",
    "Incident",
    "RiskRegister",
    "IncidentLog",
    # Response (ADR-106)
    "Citation",
    "AnswerResult",
    "KeywordMatch",
    "ReviewResult",
    # Routing (ADR-108)
    "Candidate",
    "RoutingResult",
    # Rubric (ADR-109)
    "ChecklistItem",
    "RubricColumn",
    "RubricReviewResult",
    "calculate_grade",
    "create_empty_rubric_result",
]
