"""
core/llm/config.py - LLM 설정 관리
CAP-009: LLM_CONFIG 설정 파일
ADR-104: LLM Capability Interface
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class Provider(str, Enum):
    """LLM Provider Enum"""
    MOCK = "mock"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass
class CapabilityConfig:
    """개별 Capability 설정"""
    provider: Provider = Provider.MOCK
    model: Optional[str] = None
    api_key: Optional[str] = None


@dataclass
class LLMConfig:
    """
    LLM Capability 전역 설정

    각 Capability별로 독립적인 provider/model 설정 가능
    """
    router: CapabilityConfig = field(default_factory=CapabilityConfig)
    answerer: CapabilityConfig = field(default_factory=CapabilityConfig)
    extractor: CapabilityConfig = field(default_factory=CapabilityConfig)
    judge: CapabilityConfig = field(default_factory=CapabilityConfig)

    @classmethod
    def all_mock(cls) -> "LLMConfig":
        """모든 Capability를 Mock으로 설정"""
        return cls()

    @classmethod
    def all_claude(cls, api_key: str) -> "LLMConfig":
        """모든 Capability를 Claude로 설정"""
        return cls(
            router=CapabilityConfig(
                provider=Provider.CLAUDE,
                model="claude-3-haiku-20240307",
                api_key=api_key
            ),
            answerer=CapabilityConfig(
                provider=Provider.CLAUDE,
                model="claude-sonnet-4-20250514",
                api_key=api_key
            ),
            extractor=CapabilityConfig(
                provider=Provider.CLAUDE,
                model="claude-3-haiku-20240307",
                api_key=api_key
            ),
            judge=CapabilityConfig(
                provider=Provider.CLAUDE,
                model="claude-sonnet-4-20250514",
                api_key=api_key
            ),
        )

    @classmethod
    def all_openai(cls, api_key: str) -> "LLMConfig":
        """모든 Capability를 OpenAI로 설정"""
        return cls(
            router=CapabilityConfig(
                provider=Provider.OPENAI,
                model="gpt-4o-mini",
                api_key=api_key
            ),
            answerer=CapabilityConfig(
                provider=Provider.OPENAI,
                model="gpt-4o",
                api_key=api_key
            ),
            extractor=CapabilityConfig(
                provider=Provider.OPENAI,
                model="gpt-4o-mini",
                api_key=api_key
            ),
            judge=CapabilityConfig(
                provider=Provider.OPENAI,
                model="gpt-4o",
                api_key=api_key
            ),
        )

    @classmethod
    def hybrid(
        cls,
        router_provider: Provider = Provider.MOCK,
        answerer_provider: Provider = Provider.MOCK,
        extractor_provider: Provider = Provider.MOCK,
        judge_provider: Provider = Provider.MOCK,
        claude_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ) -> "LLMConfig":
        """하이브리드 설정 (Capability별 다른 provider)"""

        def get_config(provider: Provider, capability: str) -> CapabilityConfig:
            if provider == Provider.MOCK:
                return CapabilityConfig(provider=Provider.MOCK)
            elif provider == Provider.CLAUDE:
                models = {
                    "router": "claude-3-haiku-20240307",
                    "answerer": "claude-sonnet-4-20250514",
                    "extractor": "claude-3-haiku-20240307",
                    "judge": "claude-sonnet-4-20250514",
                }
                return CapabilityConfig(
                    provider=Provider.CLAUDE,
                    model=models.get(capability),
                    api_key=claude_api_key
                )
            else:  # OPENAI
                models = {
                    "router": "gpt-4o-mini",
                    "answerer": "gpt-4o",
                    "extractor": "gpt-4o-mini",
                    "judge": "gpt-4o",
                }
                return CapabilityConfig(
                    provider=Provider.OPENAI,
                    model=models.get(capability),
                    api_key=openai_api_key
                )

        return cls(
            router=get_config(router_provider, "router"),
            answerer=get_config(answerer_provider, "answerer"),
            extractor=get_config(extractor_provider, "extractor"),
            judge=get_config(judge_provider, "judge"),
        )


# 글로벌 설정 인스턴스
_current_config: LLMConfig = LLMConfig.all_mock()


def get_config() -> LLMConfig:
    """현재 LLM 설정 반환"""
    return _current_config


def set_config(config: LLMConfig) -> None:
    """LLM 설정 변경"""
    global _current_config
    _current_config = config
