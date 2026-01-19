"""
core/llm/protocols.py - LLM Capability Protocols
CAP-002~005: Capability Protocol 정의
ADR-104: LLM Capability Interface
"""
from typing import Any, Dict, List, Protocol, runtime_checkable

from agents import TwinAgent
from schemas import KnowledgeItem, OJTTask


@runtime_checkable
class RouterCapability(Protocol):
    """
    CAP-002: 질문 → Twin 선택 인터페이스

    질문 내용을 분석하여 가장 적합한 Digital Twin을 선택합니다.
    """

    def route(self, question: str) -> str:
        """
        질문을 분석하여 적합한 Twin 이름 반환

        Args:
            question: 사용자 질문

        Returns:
            Twin 이름 (예: "Sam Lee", "Jin Park")
        """
        ...


@runtime_checkable
class AnswererCapability(Protocol):
    """
    CAP-003: Twin + 컨텍스트 → 응답 생성 인터페이스

    선택된 Twin의 페르소나로 질문에 답변합니다.
    """

    def answer(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        """
        Twin 페르소나로 응답 생성

        Args:
            twin: 선택된 TwinAgent
            org: 조직 설정
            knowledge: 관련 지식 스니펫
            question: 사용자 질문

        Returns:
            생성된 응답 문자열
        """
        ...


@runtime_checkable
class ExtractorCapability(Protocol):
    """
    CAP-004: 텍스트 → 구조화된 지식 인터페이스

    원본 텍스트에서 지식 항목을 추출합니다.
    """

    def extract(self, source: str, text: str) -> List[KnowledgeItem]:
        """
        텍스트에서 지식 항목 추출

        Args:
            source: 소스 타입 (meeting_stt, slack_discord, client_stt)
            text: 원본 텍스트

        Returns:
            추출된 KnowledgeItem 리스트
        """
        ...


@runtime_checkable
class JudgeCapability(Protocol):
    """
    CAP-005: 제출 → 평가 결과 인터페이스

    제출물을 루브릭 기준으로 평가합니다.
    """

    def judge(
        self,
        task: OJTTask,
        submission: str
    ) -> Dict[str, Any]:
        """
        제출물 평가

        Args:
            task: OJT 미션
            submission: 제출 내용

        Returns:
            평가 결과 딕셔너리:
            {
                "score": int (0-100),
                "strengths": List[str],
                "improvements": List[str],
                "next_step": str
            }
        """
        ...
