"""
core/llm - LLM Capability Layer
ADR-104: LLM Capability Interface

Capability-based LLM interface separation:
- Router: 질문 → Twin 선택
- Answerer: Twin + 컨텍스트 → 응답 생성
- Extractor: 텍스트 → 지식 추출
- Judge: 제출물 → 평가 결과
"""
from .protocols import (
    RouterCapability,
    AnswererCapability,
    ExtractorCapability,
    JudgeCapability,
)
from .config import (
    Provider,
    CapabilityConfig,
    LLMConfig,
    get_config,
    set_config,
)
from .factory import (
    create_router,
    create_answerer,
    create_extractor,
    create_judge,
    CapabilityManager,
)
from .mock import (
    MockRouter,
    MockAnswerer,
    MockExtractor,
    MockJudge,
)

__all__ = [
    # Protocols
    "RouterCapability",
    "AnswererCapability",
    "ExtractorCapability",
    "JudgeCapability",
    # Config
    "Provider",
    "CapabilityConfig",
    "LLMConfig",
    "get_config",
    "set_config",
    # Factory
    "create_router",
    "create_answerer",
    "create_extractor",
    "create_judge",
    "CapabilityManager",
    # Mock
    "MockRouter",
    "MockAnswerer",
    "MockExtractor",
    "MockJudge",
]
