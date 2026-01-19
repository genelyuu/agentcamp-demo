"""
tests/unit/test_llm_mock.py - LLM Mock Capability 단위 테스트
TEST-006: Mock Router, Answerer, Extractor, Judge 테스트
"""
import pytest

from core.llm.mock import MockRouter, MockAnswerer, MockExtractor, MockJudge
from core.llm.factory import create_router, create_answerer, create_extractor, create_judge, CapabilityManager
from core.llm.config import Provider, CapabilityConfig
from agents import get_twins
from schemas import OJTTask, KnowledgeItem, KnowledgeTag


class TestMockRouter:
    """MockRouter 테스트"""

    def test_route_returns_string(self):
        """route가 문자열을 반환하는지 테스트"""
        router = MockRouter()
        result = router.route("테스트 질문")
        assert isinstance(result, str)

    def test_route_to_sam_lee(self):
        """Sam Lee로 라우팅되는지 테스트"""
        router = MockRouter()
        result = router.route("우선순위가 어떻게 되나요?")
        assert result == "Sam Lee"

    def test_route_to_jh_kim(self):
        """JH Kim으로 라우팅되는지 테스트"""
        router = MockRouter()
        result = router.route("요구사항을 정리해주세요")
        assert result == "JH Kim"

    def test_route_to_seul_kim(self):
        """Seul Kim으로 라우팅되는지 테스트"""
        router = MockRouter()
        result = router.route("UI 컴포넌트 구조는?")
        assert result == "Seul Kim"

    def test_route_default_to_jin_park(self):
        """기본 라우팅은 Jin Park"""
        router = MockRouter()
        result = router.route("일반적인 질문")
        assert result == "Jin Park"


class TestMockAnswerer:
    """MockAnswerer 테스트"""

    def test_answer_returns_string(self):
        """answer가 문자열을 반환하는지 테스트"""
        answerer = MockAnswerer()
        twins = get_twins()
        twin = twins["Jin Park"]
        org = {"company": "Test", "role": "Engineer"}

        result = answerer.answer(twin, org, "지식", "질문")

        assert isinstance(result, str)

    def test_answer_includes_twin_name(self):
        """응답에 Twin 이름이 포함되는지 테스트"""
        answerer = MockAnswerer()
        twins = get_twins()
        twin = twins["Jin Park"]
        org = {"company": "Test", "role": "Engineer"}

        result = answerer.answer(twin, org, "", "질문")

        assert "Jin Park" in result

    def test_answer_includes_question(self):
        """응답에 질문이 포함되는지 테스트"""
        answerer = MockAnswerer()
        twins = get_twins()
        twin = twins["Jin Park"]
        org = {"company": "Test", "role": "Engineer"}

        result = answerer.answer(twin, org, "", "특별한질문")

        assert "특별한질문" in result


class TestMockExtractor:
    """MockExtractor 테스트"""

    def test_extract_returns_list(self):
        """extract가 리스트를 반환하는지 테스트"""
        extractor = MockExtractor()
        result = extractor.extract("meeting_stt", "테스트 텍스트입니다. 이것은 중요한 내용입니다.")

        assert isinstance(result, list)

    def test_extract_returns_knowledge_items(self):
        """extract가 KnowledgeItem 리스트를 반환하는지 테스트"""
        extractor = MockExtractor()
        result = extractor.extract("meeting_stt", "이것은 규칙입니다. 반드시 지켜야 합니다.")

        assert len(result) > 0
        assert all(isinstance(item, KnowledgeItem) for item in result)

    def test_extract_determines_tag(self):
        """태그가 올바르게 결정되는지 테스트"""
        extractor = MockExtractor()

        # 규칙 관련 텍스트
        result = extractor.extract("meeting_stt", "이것은 반드시 지켜야 하는 규칙입니다.")
        if result:
            assert result[0].tag == KnowledgeTag.RULE

    def test_extract_skips_short_sentences(self):
        """짧은 문장은 건너뛰는지 테스트"""
        extractor = MockExtractor()
        result = extractor.extract("meeting_stt", "짧음")

        assert len(result) == 0


class TestMockJudge:
    """MockJudge 테스트"""

    def test_judge_returns_dict(self):
        """judge가 딕셔너리를 반환하는지 테스트"""
        judge = MockJudge()
        task = OJTTask(
            id="test-001",
            title="테스트",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["원인"]
        )

        result = judge.judge(task, "원인을 분석했습니다.")

        assert isinstance(result, dict)

    def test_judge_has_score(self):
        """결과에 score가 있는지 테스트"""
        judge = MockJudge()
        task = OJTTask(
            id="test-001",
            title="테스트",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["원인"]
        )

        result = judge.judge(task, "제출")

        assert "score" in result
        assert isinstance(result["score"], int)

    def test_judge_score_range(self):
        """점수가 0-100 범위인지 테스트"""
        judge = MockJudge()
        task = OJTTask(
            id="test-001",
            title="테스트",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["원인", "로그", "재현"]
        )

        result = judge.judge(task, "원인 로그 재현 모두 포함")

        assert 0 <= result["score"] <= 100

    def test_judge_feedback_structure(self):
        """피드백 구조가 올바른지 테스트"""
        judge = MockJudge()
        task = OJTTask(
            id="test-001",
            title="테스트",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["원인"]
        )

        result = judge.judge(task, "제출")

        assert "strengths" in result
        assert "improvements" in result
        assert "next_step" in result


class TestCapabilityFactory:
    """Capability Factory 테스트"""

    def test_create_router_mock(self):
        """create_router가 MockRouter를 생성하는지 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        router = create_router(config)
        assert isinstance(router, MockRouter)

    def test_create_answerer_mock(self):
        """create_answerer가 MockAnswerer를 생성하는지 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        answerer = create_answerer(config)
        assert isinstance(answerer, MockAnswerer)

    def test_create_extractor_mock(self):
        """create_extractor가 MockExtractor를 생성하는지 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        extractor = create_extractor(config)
        assert isinstance(extractor, MockExtractor)

    def test_create_judge_mock(self):
        """create_judge가 MockJudge를 생성하는지 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        judge = create_judge(config)
        assert isinstance(judge, MockJudge)


class TestCapabilityManager:
    """CapabilityManager 테스트"""

    def test_manager_creates_capabilities(self):
        """CapabilityManager가 Capability들을 생성하는지 테스트"""
        manager = CapabilityManager()

        assert manager.router is not None
        assert manager.answerer is not None
        assert manager.extractor is not None
        assert manager.judge is not None

    def test_manager_caches_capabilities(self):
        """CapabilityManager가 Capability를 캐시하는지 테스트"""
        manager = CapabilityManager()

        router1 = manager.router
        router2 = manager.router

        assert router1 is router2

    def test_manager_reset(self):
        """CapabilityManager reset이 캐시를 초기화하는지 테스트"""
        manager = CapabilityManager()

        router1 = manager.router
        manager.reset()
        router2 = manager.router

        assert router1 is not router2
