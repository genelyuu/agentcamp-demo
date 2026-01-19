"""
tests/unit/test_orchestrator.py - Orchestrator 모듈 단위 테스트
TEST-003: 라우팅 및 응답 생성 테스트
"""
import pytest
from unittest.mock import MagicMock, patch

from core.orchestrator import (
    route_agent,
    answer_with_twin,
    set_llm_client,
    get_llm_client,
)
from agents import TwinAgent, get_twins
from llm_client import MockLLMClient


class TestRouteAgent:
    """route_agent 함수 테스트"""

    def test_route_to_sam_lee_for_priority(self):
        """우선순위 관련 질문은 Sam Lee로 라우팅"""
        result = route_agent("프로젝트 우선순위가 어떻게 되나요?")
        assert result == "Sam Lee"

    def test_route_to_sam_lee_for_strategy(self):
        """전략 관련 질문은 Sam Lee로 라우팅"""
        result = route_agent("회사 전략에 대해 알려주세요")
        assert result == "Sam Lee"

    def test_route_to_jh_kim_for_requirements(self):
        """요구사항 관련 질문은 JH Kim으로 라우팅"""
        result = route_agent("이 기능의 요구사항이 뭔가요?")
        assert result == "JH Kim"

    def test_route_to_jh_kim_for_kpi(self):
        """KPI 관련 질문은 JH Kim으로 라우팅"""
        result = route_agent("KPI 달성률은 어떻게 되나요?")
        assert result == "JH Kim"

    def test_route_to_seul_kim_for_ui(self):
        """UI 관련 질문은 Seul Kim으로 라우팅"""
        result = route_agent("UI 디자인 가이드가 있나요?")
        assert result == "Seul Kim"

    def test_route_to_seul_kim_for_frontend(self):
        """프론트엔드 관련 질문은 Seul Kim으로 라우팅"""
        result = route_agent("프론트엔드 컴포넌트 구조는?")
        assert result == "Seul Kim"

    def test_route_to_jin_park_by_default(self):
        """기본 라우팅은 Jin Park"""
        result = route_agent("API 엔드포인트를 추가하려면?")
        assert result == "Jin Park"

    def test_route_case_insensitive(self):
        """대소문자 구분 없이 라우팅"""
        result = route_agent("UI 관련 질문")
        assert result == "Seul Kim"

        result = route_agent("ui 관련 질문")
        assert result == "Seul Kim"


class TestAnswerWithTwin:
    """answer_with_twin 함수 테스트"""

    def test_answer_returns_string(self):
        """answer_with_twin이 문자열을 반환하는지 테스트"""
        twins = get_twins()
        twin = twins["Jin Park"]
        org = {"company": "Test", "role": "Engineer"}

        result = answer_with_twin(
            twin=twin,
            org=org,
            knowledge_snippets="테스트 지식",
            question="테스트 질문"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_answer_includes_twin_info(self):
        """응답에 Twin 정보가 포함되는지 테스트"""
        twins = get_twins()
        twin = twins["Jin Park"]
        org = {"company": "Test", "role": "Engineer"}

        result = answer_with_twin(
            twin=twin,
            org=org,
            knowledge_snippets="",
            question="테스트"
        )

        assert twin.name in result or twin.role in result


class TestLLMClientManagement:
    """LLM 클라이언트 관리 테스트"""

    def test_get_llm_client_returns_client(self):
        """get_llm_client가 클라이언트를 반환하는지 테스트"""
        client = get_llm_client()
        assert client is not None

    def test_set_llm_client_mock(self):
        """set_llm_client로 Mock 클라이언트 설정"""
        set_llm_client(provider="mock")
        client = get_llm_client()
        assert isinstance(client, MockLLMClient)

    def test_set_llm_client_changes_client(self):
        """set_llm_client가 클라이언트를 변경하는지 테스트"""
        original = get_llm_client()
        set_llm_client(provider="mock")
        new_client = get_llm_client()

        # Mock으로 설정했으므로 MockLLMClient 타입이어야 함
        assert isinstance(new_client, MockLLMClient)
