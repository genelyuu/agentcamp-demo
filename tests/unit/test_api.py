"""
tests/unit/test_api.py - API Facade 단위 테스트
TEST-005: AgentCampAPI 테스트
"""
import pytest

from core.api import AgentCampAPI
from schemas import OJTTask, OrgConfig, KnowledgeBase, SessionStore
from agents import TwinAgent


class TestAgentCampAPIInit:
    """AgentCampAPI 초기화 테스트"""

    def test_creates_instance(self):
        """인스턴스 생성 테스트"""
        api = AgentCampAPI()
        assert api is not None


class TestAgentCampAPIRouting:
    """AgentCampAPI 라우팅 테스트"""

    def test_route_question_returns_string(self):
        """route_question이 문자열을 반환하는지 테스트"""
        result = AgentCampAPI.route_question("테스트 질문")
        assert isinstance(result, str)

    def test_route_question_routes_correctly(self):
        """질문이 올바르게 라우팅되는지 테스트"""
        # UI 관련 질문은 Seul Kim으로
        result = AgentCampAPI.route_question("UI 디자인 가이드는?")
        assert result == "Seul Kim"

        # 기본 질문은 Jin Park으로
        result = AgentCampAPI.route_question("API 엔드포인트 추가 방법")
        assert result == "Jin Park"


class TestAgentCampAPITwins:
    """AgentCampAPI Twin 관리 테스트"""

    def test_get_twin_by_name(self):
        """이름으로 Twin을 가져오는지 테스트"""
        twin = AgentCampAPI.get_twin("Jin Park")
        assert twin is not None
        assert isinstance(twin, TwinAgent)
        assert twin.name == "Jin Park"

    def test_get_twin_nonexistent(self):
        """존재하지 않는 Twin 조회 시 None 반환"""
        twin = AgentCampAPI.get_twin("존재하지않는사람")
        assert twin is None


class TestAgentCampAPIAnswer:
    """AgentCampAPI 답변 생성 테스트"""

    def test_answer_question_returns_string(self):
        """answer_question이 문자열을 반환하는지 테스트"""
        twin = AgentCampAPI.get_twin("Jin Park")
        org = AgentCampAPI.get_organization()

        result = AgentCampAPI.answer_question(
            twin=twin,
            org=org,
            knowledge_snippets="테스트 지식",
            question="테스트 질문"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_answer_question_includes_twin_info(self):
        """응답에 Twin 정보가 포함되는지 테스트"""
        twin = AgentCampAPI.get_twin("Jin Park")
        org = AgentCampAPI.get_organization()

        result = AgentCampAPI.answer_question(
            twin=twin,
            org=org,
            knowledge_snippets="",
            question="테스트"
        )

        assert twin.name in result or twin.role in result


class TestAgentCampAPIEvaluation:
    """AgentCampAPI 평가 테스트"""

    def test_evaluate_submission_returns_tuple(self):
        """evaluate_submission이 튜플을 반환하는지 테스트"""
        task = {
            "title": "테스트 미션",
            "acceptance_keywords": ["원인", "로그"]
        }
        submission = "원인을 분석했습니다."

        result = AgentCampAPI.evaluate_submission(task, submission)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_evaluate_submission_score_and_feedback(self):
        """evaluate_submission 결과 구조 테스트"""
        task = {
            "title": "테스트",
            "acceptance_keywords": ["테스트"]
        }
        submission = "테스트 제출"

        score, feedback = AgentCampAPI.evaluate_submission(task, submission)

        assert isinstance(score, int)
        assert isinstance(feedback, dict)
        assert "strengths" in feedback
        assert "improvements" in feedback

    def test_evaluate_task_with_ojt_task(self):
        """OJTTask 모델로 평가하는지 테스트"""
        task = OJTTask(
            id="test-001",
            title="테스트 미션",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["원인"]
        )
        submission = "원인을 파악했습니다."

        score, feedback = AgentCampAPI.evaluate_task(task, submission)

        assert isinstance(score, int)
        assert isinstance(feedback, dict)


class TestAgentCampAPIStorage:
    """AgentCampAPI 저장소 테스트 (Dict 기반)"""

    def test_get_organization_returns_dict(self):
        """get_organization이 딕셔너리를 반환하는지 테스트"""
        result = AgentCampAPI.get_organization()
        assert isinstance(result, dict)
        assert "company" in result

    def test_get_knowledge_items_returns_dict(self):
        """get_knowledge_items가 딕셔너리를 반환하는지 테스트"""
        result = AgentCampAPI.get_knowledge_items()
        assert isinstance(result, dict)
        assert "items" in result

    def test_get_user_sessions_returns_dict(self):
        """get_user_sessions가 딕셔너리를 반환하는지 테스트"""
        result = AgentCampAPI.get_user_sessions()
        assert isinstance(result, dict)
        assert "users" in result


class TestAgentCampAPIPydanticStorage:
    """AgentCampAPI 저장소 테스트 (Pydantic 기반)"""

    def test_get_org_config_returns_model(self):
        """get_org_config가 OrgConfig 모델을 반환하는지 테스트"""
        result = AgentCampAPI.get_org_config()
        assert isinstance(result, OrgConfig)
        assert hasattr(result, "company")

    def test_get_knowledge_base_returns_model(self):
        """get_knowledge_base가 KnowledgeBase 모델을 반환하는지 테스트"""
        result = AgentCampAPI.get_knowledge_base()
        assert isinstance(result, KnowledgeBase)
        assert hasattr(result, "items")

    def test_get_session_store_returns_model(self):
        """get_session_store가 SessionStore 모델을 반환하는지 테스트"""
        result = AgentCampAPI.get_session_store()
        assert isinstance(result, SessionStore)
        assert hasattr(result, "users")


class TestAgentCampAPILLM:
    """AgentCampAPI LLM 설정 테스트"""

    def test_configure_llm_mock(self):
        """configure_llm으로 Mock 클라이언트 설정"""
        # 오류 없이 실행되는지 확인
        AgentCampAPI.configure_llm(provider="mock")
