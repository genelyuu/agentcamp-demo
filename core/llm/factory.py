"""
core/llm/factory.py - Capability Factory
CAP-009: Capability 인스턴스 생성 팩토리
ADR-104: LLM Capability Interface
"""
from typing import Union

from .config import Provider, CapabilityConfig, LLMConfig, get_config
from .mock import MockRouter, MockAnswerer, MockExtractor, MockJudge
from .protocols import RouterCapability, AnswererCapability, ExtractorCapability, JudgeCapability


def create_router(config: CapabilityConfig = None) -> RouterCapability:
    """Router Capability 인스턴스 생성"""
    if config is None:
        config = get_config().router

    if config.provider == Provider.MOCK:
        return MockRouter()
    elif config.provider == Provider.CLAUDE:
        from .claude import ClaudeRouter
        return ClaudeRouter(api_key=config.api_key, model=config.model)
    elif config.provider == Provider.OPENAI:
        from .openai import OpenAIRouter
        return OpenAIRouter(api_key=config.api_key, model=config.model)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")


def create_answerer(config: CapabilityConfig = None) -> AnswererCapability:
    """Answerer Capability 인스턴스 생성"""
    if config is None:
        config = get_config().answerer

    if config.provider == Provider.MOCK:
        return MockAnswerer()
    elif config.provider == Provider.CLAUDE:
        from .claude import ClaudeAnswerer
        return ClaudeAnswerer(api_key=config.api_key, model=config.model)
    elif config.provider == Provider.OPENAI:
        from .openai import OpenAIAnswerer
        return OpenAIAnswerer(api_key=config.api_key, model=config.model)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")


def create_extractor(config: CapabilityConfig = None) -> ExtractorCapability:
    """Extractor Capability 인스턴스 생성"""
    if config is None:
        config = get_config().extractor

    if config.provider == Provider.MOCK:
        return MockExtractor()
    elif config.provider == Provider.CLAUDE:
        from .claude import ClaudeExtractor
        return ClaudeExtractor(api_key=config.api_key, model=config.model)
    elif config.provider == Provider.OPENAI:
        from .openai import OpenAIExtractor
        return OpenAIExtractor(api_key=config.api_key, model=config.model)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")


def create_judge(config: CapabilityConfig = None) -> JudgeCapability:
    """Judge Capability 인스턴스 생성"""
    if config is None:
        config = get_config().judge

    if config.provider == Provider.MOCK:
        return MockJudge()
    elif config.provider == Provider.CLAUDE:
        from .claude import ClaudeJudge
        return ClaudeJudge(api_key=config.api_key, model=config.model)
    elif config.provider == Provider.OPENAI:
        from .openai import OpenAIJudge
        return OpenAIJudge(api_key=config.api_key, model=config.model)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")


class CapabilityManager:
    """
    Capability 인스턴스 관리자

    설정에 따라 각 Capability 인스턴스를 생성하고 관리합니다.
    """

    def __init__(self, config: LLMConfig = None):
        self.config = config or get_config()
        self._router = None
        self._answerer = None
        self._extractor = None
        self._judge = None

    @property
    def router(self) -> RouterCapability:
        if self._router is None:
            self._router = create_router(self.config.router)
        return self._router

    @property
    def answerer(self) -> AnswererCapability:
        if self._answerer is None:
            self._answerer = create_answerer(self.config.answerer)
        return self._answerer

    @property
    def extractor(self) -> ExtractorCapability:
        if self._extractor is None:
            self._extractor = create_extractor(self.config.extractor)
        return self._extractor

    @property
    def judge(self) -> JudgeCapability:
        if self._judge is None:
            self._judge = create_judge(self.config.judge)
        return self._judge

    def reset(self) -> None:
        """캐시된 인스턴스 초기화"""
        self._router = None
        self._answerer = None
        self._extractor = None
        self._judge = None
