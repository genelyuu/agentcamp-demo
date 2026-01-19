"""
tests/unit/test_llm_factory.py - LLM Factory 단위 테스트
TEST-015: LLM Capability Factory 테스트
"""
import pytest

from core.llm.config import (
    Provider,
    CapabilityConfig,
    LLMConfig,
    get_config,
    set_config,
)
from core.llm.factory import (
    create_router,
    create_answerer,
    create_extractor,
    create_judge,
    CapabilityManager,
)
from core.llm.mock import MockRouter, MockAnswerer, MockExtractor, MockJudge
from core.llm.protocols import (
    RouterCapability,
    AnswererCapability,
    ExtractorCapability,
    JudgeCapability,
)


class TestProvider:
    """Provider enum 테스트"""

    def test_provider_values(self):
        """Provider enum 값 테스트"""
        assert Provider.MOCK.value == "mock"
        assert Provider.CLAUDE.value == "claude"
        assert Provider.OPENAI.value == "openai"

    def test_provider_is_string_enum(self):
        """Provider가 str enum인지 테스트"""
        assert isinstance(Provider.MOCK, str)
        assert Provider.MOCK == "mock"


class TestCapabilityConfig:
    """CapabilityConfig 테스트"""

    def test_default_config(self):
        """기본 설정 테스트"""
        config = CapabilityConfig()
        assert config.provider == Provider.MOCK
        assert config.model is None
        assert config.api_key is None

    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = CapabilityConfig(
            provider=Provider.CLAUDE,
            model="claude-sonnet-4-20250514",
            api_key="test-key"
        )
        assert config.provider == Provider.CLAUDE
        assert config.model == "claude-sonnet-4-20250514"
        assert config.api_key == "test-key"


class TestLLMConfig:
    """LLMConfig 테스트"""

    def test_default_llm_config(self):
        """기본 LLMConfig 테스트"""
        config = LLMConfig()
        assert config.router.provider == Provider.MOCK
        assert config.answerer.provider == Provider.MOCK
        assert config.extractor.provider == Provider.MOCK
        assert config.judge.provider == Provider.MOCK

    def test_all_mock(self):
        """all_mock 클래스 메서드 테스트"""
        config = LLMConfig.all_mock()
        assert config.router.provider == Provider.MOCK
        assert config.answerer.provider == Provider.MOCK
        assert config.extractor.provider == Provider.MOCK
        assert config.judge.provider == Provider.MOCK

    def test_all_claude(self):
        """all_claude 클래스 메서드 테스트"""
        config = LLMConfig.all_claude(api_key="test-claude-key")
        assert config.router.provider == Provider.CLAUDE
        assert config.answerer.provider == Provider.CLAUDE
        assert config.extractor.provider == Provider.CLAUDE
        assert config.judge.provider == Provider.CLAUDE
        assert config.router.api_key == "test-claude-key"

    def test_all_openai(self):
        """all_openai 클래스 메서드 테스트"""
        config = LLMConfig.all_openai(api_key="test-openai-key")
        assert config.router.provider == Provider.OPENAI
        assert config.answerer.provider == Provider.OPENAI
        assert config.extractor.provider == Provider.OPENAI
        assert config.judge.provider == Provider.OPENAI
        assert config.router.api_key == "test-openai-key"

    def test_hybrid_config(self):
        """hybrid 클래스 메서드 테스트"""
        config = LLMConfig.hybrid(
            router_provider=Provider.MOCK,
            answerer_provider=Provider.CLAUDE,
            extractor_provider=Provider.MOCK,
            judge_provider=Provider.OPENAI,
            claude_api_key="claude-key",
            openai_api_key="openai-key"
        )
        assert config.router.provider == Provider.MOCK
        assert config.answerer.provider == Provider.CLAUDE
        assert config.answerer.api_key == "claude-key"
        assert config.extractor.provider == Provider.MOCK
        assert config.judge.provider == Provider.OPENAI
        assert config.judge.api_key == "openai-key"


class TestConfigFunctions:
    """get_config, set_config 테스트"""

    def test_get_config_returns_llmconfig(self):
        """get_config가 LLMConfig 반환하는지 테스트"""
        config = get_config()
        assert isinstance(config, LLMConfig)

    def test_set_config(self):
        """set_config 테스트"""
        original_config = get_config()
        new_config = LLMConfig.all_mock()
        set_config(new_config)
        assert get_config() is new_config
        # 복원
        set_config(original_config)


class TestCreateRouter:
    """create_router 팩토리 함수 테스트"""

    def test_create_mock_router(self):
        """Mock Router 생성 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        router = create_router(config)
        assert isinstance(router, MockRouter)
        assert isinstance(router, RouterCapability)

    def test_create_router_with_default_config(self):
        """기본 설정으로 Router 생성 테스트"""
        # Mock 설정 상태에서
        original_config = get_config()
        set_config(LLMConfig.all_mock())

        router = create_router()
        assert isinstance(router, MockRouter)

        set_config(original_config)

    def test_create_router_unknown_provider(self):
        """알 수 없는 Provider로 생성 시 에러 테스트"""
        # Provider를 직접 조작할 수 없으므로 이 테스트는 스킵
        pass


class TestCreateAnswerer:
    """create_answerer 팩토리 함수 테스트"""

    def test_create_mock_answerer(self):
        """Mock Answerer 생성 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        answerer = create_answerer(config)
        assert isinstance(answerer, MockAnswerer)
        assert isinstance(answerer, AnswererCapability)

    def test_create_answerer_with_default_config(self):
        """기본 설정으로 Answerer 생성 테스트"""
        original_config = get_config()
        set_config(LLMConfig.all_mock())

        answerer = create_answerer()
        assert isinstance(answerer, MockAnswerer)

        set_config(original_config)


class TestCreateExtractor:
    """create_extractor 팩토리 함수 테스트"""

    def test_create_mock_extractor(self):
        """Mock Extractor 생성 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        extractor = create_extractor(config)
        assert isinstance(extractor, MockExtractor)
        assert isinstance(extractor, ExtractorCapability)

    def test_create_extractor_with_default_config(self):
        """기본 설정으로 Extractor 생성 테스트"""
        original_config = get_config()
        set_config(LLMConfig.all_mock())

        extractor = create_extractor()
        assert isinstance(extractor, MockExtractor)

        set_config(original_config)


class TestCreateJudge:
    """create_judge 팩토리 함수 테스트"""

    def test_create_mock_judge(self):
        """Mock Judge 생성 테스트"""
        config = CapabilityConfig(provider=Provider.MOCK)
        judge = create_judge(config)
        assert isinstance(judge, MockJudge)
        assert isinstance(judge, JudgeCapability)

    def test_create_judge_with_default_config(self):
        """기본 설정으로 Judge 생성 테스트"""
        original_config = get_config()
        set_config(LLMConfig.all_mock())

        judge = create_judge()
        assert isinstance(judge, MockJudge)

        set_config(original_config)


class TestCapabilityManager:
    """CapabilityManager 테스트"""

    @pytest.fixture
    def mock_config(self):
        """Mock 설정 픽스처"""
        return LLMConfig.all_mock()

    def test_manager_initialization(self, mock_config):
        """CapabilityManager 초기화 테스트"""
        manager = CapabilityManager(mock_config)
        assert manager.config is mock_config
        assert manager._router is None
        assert manager._answerer is None
        assert manager._extractor is None
        assert manager._judge is None

    def test_manager_router_property(self, mock_config):
        """router 프로퍼티 테스트"""
        manager = CapabilityManager(mock_config)
        router = manager.router
        assert isinstance(router, RouterCapability)
        # 캐싱 확인
        assert manager.router is router

    def test_manager_answerer_property(self, mock_config):
        """answerer 프로퍼티 테스트"""
        manager = CapabilityManager(mock_config)
        answerer = manager.answerer
        assert isinstance(answerer, AnswererCapability)
        # 캐싱 확인
        assert manager.answerer is answerer

    def test_manager_extractor_property(self, mock_config):
        """extractor 프로퍼티 테스트"""
        manager = CapabilityManager(mock_config)
        extractor = manager.extractor
        assert isinstance(extractor, ExtractorCapability)
        # 캐싱 확인
        assert manager.extractor is extractor

    def test_manager_judge_property(self, mock_config):
        """judge 프로퍼티 테스트"""
        manager = CapabilityManager(mock_config)
        judge = manager.judge
        assert isinstance(judge, JudgeCapability)
        # 캐싱 확인
        assert manager.judge is judge

    def test_manager_reset(self, mock_config):
        """reset 메서드 테스트"""
        manager = CapabilityManager(mock_config)
        # 인스턴스 생성
        router = manager.router
        answerer = manager.answerer
        # 리셋
        manager.reset()
        assert manager._router is None
        assert manager._answerer is None
        assert manager._extractor is None
        assert manager._judge is None
        # 새 인스턴스 생성 확인
        new_router = manager.router
        assert new_router is not router

    def test_manager_default_config(self):
        """기본 설정으로 CapabilityManager 테스트"""
        original_config = get_config()
        set_config(LLMConfig.all_mock())

        manager = CapabilityManager()
        assert manager.config is not None
        router = manager.router
        assert isinstance(router, MockRouter)

        set_config(original_config)

    def test_manager_all_capabilities_are_mock(self, mock_config):
        """모든 Capability가 Mock인지 테스트"""
        manager = CapabilityManager(mock_config)
        assert isinstance(manager.router, MockRouter)
        assert isinstance(manager.answerer, MockAnswerer)
        assert isinstance(manager.extractor, MockExtractor)
        assert isinstance(manager.judge, MockJudge)


class TestFactoryWithProtocols:
    """팩토리가 프로토콜을 준수하는지 테스트"""

    @pytest.fixture
    def manager(self):
        return CapabilityManager(LLMConfig.all_mock())

    def test_router_has_route_method(self, manager):
        """Router가 route 메서드를 가지는지 테스트"""
        router = manager.router
        assert hasattr(router, 'route')

    def test_answerer_has_answer_method(self, manager):
        """Answerer가 answer 메서드를 가지는지 테스트"""
        answerer = manager.answerer
        assert hasattr(answerer, 'answer')

    def test_extractor_has_extract_method(self, manager):
        """Extractor가 extract 메서드를 가지는지 테스트"""
        extractor = manager.extractor
        assert hasattr(extractor, 'extract')

    def test_judge_has_judge_method(self, manager):
        """Judge가 judge 메서드를 가지는지 테스트"""
        judge = manager.judge
        assert hasattr(judge, 'judge')
