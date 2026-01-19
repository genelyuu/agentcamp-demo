"""
orchestrator.py - 질문 라우팅 & 답변 생성 모듈 (Backward Compatibility Wrapper)
ARCH-007: 기존 모듈 래퍼 유지
참조: core/orchestrator.py
"""
from core.orchestrator import (
    route_agent,
    answer_with_twin,
    set_llm_client,
    get_llm_client,
)

__all__ = [
    "route_agent",
    "answer_with_twin",
    "set_llm_client",
    "get_llm_client",
]
