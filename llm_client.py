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
    """Mock LLM 클라이언트 (API 키 없이 동작) - ADR-107: 트윈별 차별화 응답"""

    def generate_response(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        """트윈별 차별화된 응답 포맷 적용 (ADR-107)"""
        fmt = twin.response_format
        lines = []

        # 헤더 (트윈별 이모지 포함)
        emoji = fmt.emoji if fmt else ""
        lines.append(f"{emoji} [{twin.name} | {twin.role}]")

        # 인사말 (트윈별 톤)
        if fmt and fmt.greeting:
            lines.append(f"\n{fmt.greeting}")

        lines.append(f"\n📝 질문: {question}")

        # 회사 지식 인용 (있는 경우)
        if knowledge:
            lines.append(f"\n💡 참고 지식: {knowledge[:200]}...")

        # 트윈별 섹션 구조
        if fmt and fmt.sections:
            lines.append("")
            for i, section in enumerate(fmt.sections, 1):
                lines.append(f"**{i}. {section}**")
                lines.append(self._generate_section_content(twin.name, section, question))
                lines.append("")
        else:
            # 기본 포맷 (폴백)
            lines.extend([
                "",
                "**핵심 포인트:**",
                "- 완료 기준을 명확히 정의하세요",
                "- 근거(로그/메트릭)를 확보하세요",
                "- 작은 단위로 검증하세요",
            ])

        # 주의사항 (트윈별 의사결정 규칙)
        if twin.decision_rules:
            lines.append(f"⚠️ 주의: {twin.decision_rules[0]}")

        # 마무리 (트윈별 클로징)
        if fmt and fmt.closing:
            lines.append(f"\n{fmt.closing}")

        return "\n".join(lines)

    def _generate_section_content(self, twin_name: str, section: str, question: str) -> str:
        """섹션별 내용 생성 (트윈별 차별화)"""
        # Sam Lee (CEO) - 결론 중심
        if twin_name == "Sam Lee":
            contents = {
                "결론": "→ 고객 가치가 명확하면 진행, 불명확하면 검증부터",
                "근거": "→ 비용/속도/품질 중 우선순위를 정해서 판단",
                "리스크": "→ 리스크는 회피가 아닌 관리 대상",
                "다음 액션": "→ 오늘 중 검증 가능한 최소 단위로 실행",
            }
        # JH Kim (PM) - 체크리스트
        elif twin_name == "JH Kim":
            contents = {
                "문제 정의": "→ '무엇이 문제인가?'를 한 문장으로 정리",
                "성공 조건": "→ 완료 기준을 측정 가능하게 정의\n  □ 기준1: _____\n  □ 기준2: _____",
                "체크리스트": "→ 실행 항목:\n  □ 데이터/로그 확인\n  □ 재현 조건 정리\n  □ 해결안 1개 이상 도출",
                "우선순위": "→ 지금 당장 할 것 vs 나중에 할 것 분리",
            }
        # Seul Kim (Frontend) - UX 중심
        elif twin_name == "Seul Kim":
            contents = {
                "사용자 흐름": "→ 사용자가 이 기능을 어떻게 사용하나요?\n  1) 진입점 → 2) 액션 → 3) 결과 확인",
                "에러 케이스": "→ 예외 상황 체크:\n  • 빈 값 입력 시?\n  • 네트워크 오류 시?\n  • 권한 없을 때?",
                "구현 포인트": "→ 최소 변경으로 최대 효과 내는 방법 고민",
                "개선 제안": "→ 사용자 피드백을 즉시 보여주는 UI 고려",
            }
        # Jin Park (Backend) - 분석적
        else:
            contents = {
                "현상 분석": "→ 로그/메트릭에서 관찰된 현상 정리\n  • 언제 발생? • 빈도는? • 영향 범위는?",
                "원인 가설": "→ 가능한 원인 나열:\n  1) 가설A: _____\n  2) 가설B: _____",
                "검증 방법": "→ 각 가설을 검증할 방법:\n  • 로그 쿼리: _____\n  • 재현 단계: _____",
                "해결 방안": "→ 단기 해결 vs 장기 개선 분리\n  • 핫픽스: _____\n  • 근본 해결: _____",
            }

        return contents.get(section, "→ (내용을 작성하세요)")


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
        # ADR-107: 트윈별 응답 포맷 포함
        fmt = twin.response_format
        format_instruction = ""
        if fmt and fmt.sections:
            format_instruction = f"""
[응답 포맷]
{fmt.emoji} 시작하고, 다음 섹션 구조를 따르세요:
{chr(10).join(f'{i}. {s}' for i, s in enumerate(fmt.sections, 1))}

마무리: {fmt.closing}
톤: {fmt.tone}
"""
        return f"""당신은 {org.get('company', 'Veluga')} 회사의 {twin.name}입니다.

[역할] {twin.role}
[커뮤니케이션 스타일] {twin.style}

[책임 영역]
{chr(10).join(f'- {r}' for r in twin.responsibilities)}

[의사결정 규칙]
{chr(10).join(f'- {r}' for r in twin.decision_rules)}
{format_instruction}
[회사 지식/컨텍스트]
{knowledge if knowledge else '(없음)'}

[지시사항]
- 신입 직원의 OJT를 돕는 멘토 역할을 합니다.
- 질문에 대해 당신의 역할과 스타일에 맞게 답변하세요.
- 지정된 응답 포맷을 따르세요.
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
        # ADR-107: 트윈별 응답 포맷 포함
        fmt = twin.response_format
        format_instruction = ""
        if fmt and fmt.sections:
            format_instruction = f"""
[응답 포맷]
{fmt.emoji} 시작하고, 다음 섹션 구조를 따르세요:
{chr(10).join(f'{i}. {s}' for i, s in enumerate(fmt.sections, 1))}

마무리: {fmt.closing}
톤: {fmt.tone}
"""
        return f"""당신은 {org.get('company', 'Veluga')} 회사의 {twin.name}입니다.

[역할] {twin.role}
[커뮤니케이션 스타일] {twin.style}

[책임 영역]
{chr(10).join(f'- {r}' for r in twin.responsibilities)}

[의사결정 규칙]
{chr(10).join(f'- {r}' for r in twin.decision_rules)}
{format_instruction}
[회사 지식/컨텍스트]
{knowledge if knowledge else '(없음)'}

[지시사항]
- 신입 직원의 OJT를 돕는 멘토 역할을 합니다.
- 질문에 대해 당신의 역할과 스타일에 맞게 답변하세요.
- 지정된 응답 포맷을 따르세요.
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
