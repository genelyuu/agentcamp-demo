"""
core/orchestrator.py - 질문 라우팅 & 답변 생성 모듈
ARCH-003: orchestrator.py → core/ 마이그레이션
ADR-101: UI/Core Boundary Separation
LOG-003: 로깅 적용
"""
import time
from typing import Any, Dict, Optional

from agents import TwinAgent
from llm_client import BaseLLMClient, MockLLMClient, create_llm_client

from .logger import get_logger

logger = get_logger("orchestrator")

# 라우팅 키워드 정의
_ROUTING_RULES: Dict[str, list[str]] = {
    "Sam Lee": ["우선순위", "전략", "고객", "리스크", "비용"],
    "JH Kim": ["요구사항", "스코프", "정의", "kpi", "지표"],
    "Seul Kim": ["ui", "ux", "화면", "프론트", "component", "반응형"],
}

# 글로벌 LLM 클라이언트 (기본: Mock)
_llm_client: BaseLLMClient = MockLLMClient()


def set_llm_client(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> None:
    """
    LLM 클라이언트 설정

    Args:
        provider: "mock", "claude", "openai"
        api_key: API 키
        model: 모델명 (선택)
    """
    global _llm_client
    logger.info(f"Setting LLM client: provider={provider}, model={model or 'default'}")
    _llm_client = create_llm_client(provider, api_key, model)
    logger.info(f"LLM client set successfully: {type(_llm_client).__name__}")


def get_llm_client() -> BaseLLMClient:
    """현재 LLM 클라이언트 반환"""
    return _llm_client


def route_agent(question: str) -> str:
    """
    질문 내용 기반 Digital Twin 라우팅

    Args:
        question: 사용자 질문

    Returns:
        선택된 Twin 이름
    """
    q_lower = question.lower()

    for twin_name, keywords in _ROUTING_RULES.items():
        if any(kw in q_lower for kw in keywords):
            logger.debug(f"Routed to {twin_name}: question='{question[:50]}...'")
            return twin_name

    # 기본값: Backend (Jin Park)
    logger.debug(f"Default routing to Jin Park: question='{question[:50]}...'")
    return "Jin Park"


def answer_with_twin(
    twin: TwinAgent,
    org: Dict[str, Any],
    knowledge_snippets: str,
    question: str,
    llm_client: Optional[BaseLLMClient] = None
) -> str:
    """
    Digital Twin으로 답변 생성

    Args:
        twin: TwinAgent 인스턴스
        org: 조직 설정
        knowledge_snippets: 관련 지식 스니펫
        question: 사용자 질문
        llm_client: LLM 클라이언트 (없으면 글로벌 클라이언트 사용)

    Returns:
        답변 문자열
    """
    client = llm_client or _llm_client
    client_name = type(client).__name__

    logger.info(f"Generating answer: twin={twin.name}, client={client_name}")
    start_time = time.time()

    try:
        response = client.generate_response(twin, org, knowledge_snippets, question)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Answer generated: twin={twin.name}, duration={duration_ms:.2f}ms, length={len(response)}")
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Answer generation failed: twin={twin.name}, error={str(e)}, duration={duration_ms:.2f}ms")
        raise
