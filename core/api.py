"""
core/api.py - UI/Core 경계 계약 (Facade)
ARCH-002: AgentCampAPI Boundary Contract
ADR-101: UI/Core Boundary Separation
ERR-API-001~008: Instance-based API 추가

이 모듈은 app.py(UI)와 core 비즈니스 로직 사이의
유일한 진입점 역할을 수행합니다.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from agents import TwinAgent, get_twins
from schemas import (
    OrgConfig,
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeTag,
    KnowledgeSource,
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

    Instance-based API와 Static API 모두 지원합니다.
    """

    # ===================
    # Instance Initialization (ERR-API-001, ERR-API-002)
    # ===================

    def __init__(self) -> None:
        """인스턴스 초기화 - twins, org 속성 설정"""
        self.twins: Dict[str, TwinAgent] = get_twins()
        self.org: Dict[str, Any] = get_org()
        self._knowledge: Dict[str, Any] = get_knowledge()

    # ===================
    # Instance Methods - Chat (ERR-API-003)
    # ===================

    def ask(self, question: str) -> Dict[str, Any]:
        """
        질문에 대한 답변을 반환하는 convenience method

        Args:
            question: 사용자 질문

        Returns:
            {"twin": twin_name, "answer": answer_text}
        """
        twin_name = route_agent(question)
        twin = self.twins.get(twin_name)

        if twin is None:
            twin = self.twins.get("Jin Park")  # Fallback

        # 지식 스니펫 조회
        knowledge_snippets = self.get_knowledge_snippets(question)

        # 답변 생성
        answer = answer_with_twin(twin, self.org, knowledge_snippets, question)

        return {
            "twin": twin_name,
            "answer": answer
        }

    # ===================
    # Instance Methods - Review (ERR-API-004, ERR-API-005)
    # ===================

    def review_submission(
        self,
        task: Dict[str, Any],
        submission: str
    ) -> Dict[str, Any]:
        """
        제출물 평가 (Dict task 기반)

        Args:
            task: 태스크 정보 dict (title, acceptance_keywords 등)
            submission: 제출물 텍스트

        Returns:
            {"score": int, "feedback": dict}
        """
        score, feedback = simple_review(task, submission)
        return {
            "score": score,
            "feedback": feedback
        }

    def review_with_task(
        self,
        task: OJTTask,
        submission: str
    ) -> Dict[str, Any]:
        """
        제출물 평가 (OJTTask 모델 기반)

        Args:
            task: OJTTask Pydantic 모델
            submission: 제출물 텍스트

        Returns:
            {"score": int, "feedback": dict}
        """
        score, feedback = review_with_task(task, submission)
        return {
            "score": score,
            "feedback": feedback
        }

    # ===================
    # Instance Methods - Twins (ERR-API-006)
    # ===================

    def list_twins(self) -> List[TwinAgent]:
        """
        모든 Digital Twin 목록 반환

        Returns:
            TwinAgent 리스트
        """
        return list(self.twins.values())

    # ===================
    # Instance Methods - Knowledge (ERR-API-007, ERR-API-008)
    # ===================

    def get_knowledge_snippets(self, query: str) -> str:
        """
        질문과 관련된 지식 스니펫 조회

        Args:
            query: 검색 쿼리

        Returns:
            관련 지식 스니펫 문자열
        """
        knowledge = get_knowledge()
        items = knowledge.get("items", [])

        if not items:
            return ""

        # 간단한 키워드 매칭으로 관련 스니펫 필터링
        query_lower = query.lower()
        relevant = []

        for item in items:
            text = item.get("text", "")
            if any(word in text.lower() for word in query_lower.split()):
                relevant.append(text)

        # 최대 3개 스니펫 반환
        return "\n".join(relevant[:3])

    def add_knowledge(
        self,
        source: str,
        text: str,
        tag: str = "rule"
    ) -> Dict[str, Any]:
        """
        지식 항목 추가

        Args:
            source: 지식 소스 (meeting_stt, slack_discord, client_stt)
            text: 지식 내용
            tag: 지식 태그 (rule, pitfall, glossary, process)

        Returns:
            {"id": str, "count": int} 추가된 항목 정보
        """
        knowledge = get_knowledge()
        items = knowledge.get("items", [])

        # 새 항목 생성
        new_id = f"K-{uuid4().hex[:8].upper()}"
        new_item = {
            "id": new_id,
            "text": text,
            "tag": tag,
            "source": source,
            "created_at": None  # storage에서 처리
        }

        items.append(new_item)
        knowledge["items"] = items
        set_knowledge(knowledge)

        return {
            "id": new_id,
            "count": len(items)
        }

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
