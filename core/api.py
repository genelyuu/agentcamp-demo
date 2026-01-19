"""
core/api.py - UI/Core 경계 계약 (Facade)
ARCH-002: AgentCampAPI Boundary Contract
ADR-101: UI/Core Boundary Separation

이 모듈은 app.py(UI)와 core 비즈니스 로직 사이의
유일한 진입점 역할을 수행합니다.
"""
from typing import Any, Dict, Optional, Tuple

from agents import TwinAgent, get_twins
from schemas import (
    OrgConfig,
    KnowledgeBase,
    UserSession,
    SessionStore,
    OJTTask,
    ChatMessage,
    AuditEvent,
)

from .orchestrator import (
    route_agent,
    answer_with_twin,
    set_llm_client,
    get_llm_client,
)
from .evaluation import simple_review, review_with_task
from .storage import (
    get_org,
    set_org,
    get_knowledge,
    set_knowledge,
    get_sessions,
    set_sessions,
    get_org_config,
    set_org_config,
    get_knowledge_base,
    set_knowledge_base,
    get_session_store,
    set_session_store,
)


class AgentCampAPI:
    """
    AgentCamp UI/Core 경계 Facade

    ADR-101에 따른 단일 진입점으로,
    UI 레이어는 이 클래스를 통해서만 비즈니스 로직에 접근합니다.
    """

    # ===================
    # LLM 클라이언트 설정
    # ===================

    @staticmethod
    def configure_llm(
        provider: str = "mock",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """LLM 프로바이더 설정"""
        set_llm_client(provider, api_key, model)

    # ===================
    # 질문 라우팅 & 답변
    # ===================

    @staticmethod
    def route_question(question: str) -> str:
        """질문 기반 Digital Twin 라우팅"""
        return route_agent(question)

    @staticmethod
    def get_twin(name: str) -> Optional[TwinAgent]:
        """이름으로 TwinAgent 조회"""
        return get_twins().get(name)

    @staticmethod
    def answer_question(
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge_snippets: str,
        question: str
    ) -> str:
        """Digital Twin으로 답변 생성"""
        return answer_with_twin(twin, org, knowledge_snippets, question)

    # ===================
    # 제출물 평가
    # ===================

    @staticmethod
    def evaluate_submission(
        task: Dict[str, Any],
        submission: str
    ) -> Tuple[int, Dict[str, Any]]:
        """루브릭 기반 제출물 평가"""
        return simple_review(task, submission)

    @staticmethod
    def evaluate_task(
        task: OJTTask,
        submission: str
    ) -> Tuple[int, Dict[str, Any]]:
        """OJTTask 기반 제출물 평가"""
        return review_with_task(task, submission)

    # ===================
    # 데이터 저장소 (Dict 기반 - 기존 호환)
    # ===================

    @staticmethod
    def get_organization() -> Dict[str, Any]:
        """조직 설정 조회"""
        return get_org()

    @staticmethod
    def set_organization(org: Dict[str, Any]) -> None:
        """조직 설정 저장"""
        set_org(org)

    @staticmethod
    def get_knowledge_items() -> Dict[str, Any]:
        """지식 베이스 조회"""
        return get_knowledge()

    @staticmethod
    def set_knowledge_items(knowledge: Dict[str, Any]) -> None:
        """지식 베이스 저장"""
        set_knowledge(knowledge)

    @staticmethod
    def get_user_sessions() -> Dict[str, Any]:
        """세션 정보 조회"""
        return get_sessions()

    @staticmethod
    def set_user_sessions(sessions: Dict[str, Any]) -> None:
        """세션 정보 저장"""
        set_sessions(sessions)

    # ===================
    # 데이터 저장소 (Pydantic 기반 - 신규)
    # ===================

    @staticmethod
    def get_org_config() -> OrgConfig:
        """OrgConfig Pydantic 모델로 조회"""
        return get_org_config()

    @staticmethod
    def set_org_config(config: OrgConfig) -> None:
        """OrgConfig Pydantic 모델로 저장"""
        set_org_config(config)

    @staticmethod
    def get_knowledge_base() -> KnowledgeBase:
        """KnowledgeBase Pydantic 모델로 조회"""
        return get_knowledge_base()

    @staticmethod
    def set_knowledge_base(kb: KnowledgeBase) -> None:
        """KnowledgeBase Pydantic 모델로 저장"""
        set_knowledge_base(kb)

    @staticmethod
    def get_session_store() -> SessionStore:
        """SessionStore Pydantic 모델로 조회"""
        return get_session_store()

    @staticmethod
    def set_session_store(store: SessionStore) -> None:
        """SessionStore Pydantic 모델로 저장"""
        set_session_store(store)
