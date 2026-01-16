"""
llm_client.py - LLM 클라이언트 추상화 모듈
책임: Claude/OpenAI API 통합 및 Mock 모드 지원
"""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from agents import TwinAgent


class BaseLLMClient(ABC):
    """LLM 클라이언트 추상 베이스 클래스"""

    @abstractmethod
    def generate_response(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        """Twin 페르소나로 응답 생성"""
        pass


class MockLLMClient(BaseLLMClient):
    """Mock LLM 클라이언트 (API 키 없이 동작)"""

    def generate_response(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        lines = [
            f"[{twin.name} | {twin.role}]",
            f"스타일: {twin.style}",
            "",
            f"질문: {question}",
            "",
            "내가 보는 핵심:",
        ]

        if knowledge:
            lines.append(f"- (회사 지식 참고) {knowledge[:280]}")

        lines.extend([
            "",
            "권장 액션(오늘 OJT 관점):",
            "1) 완료 기준을 1문장으로 다시 쓰기",
            "2) 지금 가진 근거(로그/스크린샷/재현단계)를 붙이기",
            "3) 10분 안에 검증 가능한 다음 스텝 실행",
            "",
            "주의:",
            f"- {twin.decision_rules[0] if twin.decision_rules else '근거 기반 판단'}",
        ])

        return "\n".join(lines)


class ClaudeLLMClient(BaseLLMClient):
    """Anthropic Claude LLM 클라이언트"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("anthropic 패키지를 설치하세요: pip install anthropic")

    def generate_response(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        system_prompt = self._build_system_prompt(twin, org, knowledge)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": question}]
            )
            return response.content[0].text
        except Exception as e:
            return f"[Claude API 오류] {str(e)}"

    def _build_system_prompt(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str
    ) -> str:
        return f"""당신은 {org.get('company', 'Veluga')} 회사의 {twin.name}입니다.

[역할] {twin.role}
[커뮤니케이션 스타일] {twin.style}

[책임 영역]
{chr(10).join(f'- {r}' for r in twin.responsibilities)}

[의사결정 규칙]
{chr(10).join(f'- {r}' for r in twin.decision_rules)}

[회사 지식/컨텍스트]
{knowledge if knowledge else '(없음)'}

[지시사항]
- 신입 직원의 OJT를 돕는 멘토 역할을 합니다.
- 질문에 대해 당신의 역할과 스타일에 맞게 답변하세요.
- 구체적이고 실행 가능한 조언을 제공하세요.
- 한국어로 답변하세요."""


class OpenAILLMClient(BaseLLMClient):
    """OpenAI GPT LLM 클라이언트"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

    def generate_response(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        system_prompt = self._build_system_prompt(twin, org, knowledge)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI API 오류] {str(e)}"

    def _build_system_prompt(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str
    ) -> str:
        return f"""당신은 {org.get('company', 'Veluga')} 회사의 {twin.name}입니다.

[역할] {twin.role}
[커뮤니케이션 스타일] {twin.style}

[책임 영역]
{chr(10).join(f'- {r}' for r in twin.responsibilities)}

[의사결정 규칙]
{chr(10).join(f'- {r}' for r in twin.decision_rules)}

[회사 지식/컨텍스트]
{knowledge if knowledge else '(없음)'}

[지시사항]
- 신입 직원의 OJT를 돕는 멘토 역할을 합니다.
- 질문에 대해 당신의 역할과 스타일에 맞게 답변하세요.
- 구체적이고 실행 가능한 조언을 제공하세요.
- 한국어로 답변하세요."""


def create_llm_client(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMClient:
    """
    LLM 클라이언트 팩토리 함수

    Args:
        provider: "mock", "claude", "openai"
        api_key: API 키 (mock 제외)
        model: 모델명 (선택)

    Returns:
        BaseLLMClient 인스턴스
    """
    if provider == "mock":
        return MockLLMClient()

    if not api_key:
        raise ValueError(f"{provider} 사용을 위해 API 키가 필요합니다.")

    if provider == "claude":
        return ClaudeLLMClient(
            api_key=api_key,
            model=model or "claude-sonnet-4-20250514"
        )
    elif provider == "openai":
        return OpenAILLMClient(
            api_key=api_key,
            model=model or "gpt-4o"
        )
    else:
        raise ValueError(f"지원하지 않는 provider: {provider}")
