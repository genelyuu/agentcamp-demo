"""
orchestrator.py - 질문 라우팅 & 답변 생성 모듈
책임: 질문 기반 Twin 라우팅 및 Mock/LLM 답변 생성
"""
from typing import Any, Dict

from agents import TwinAgent

# 라우팅 키워드 정의
_ROUTING_RULES = {
    "Sam Lee": ["우선순위", "전략", "고객", "리스크", "비용"],
    "JH Kim": ["요구사항", "스코프", "정의", "kpi", "지표"],
    "Seul Kim": ["ui", "ux", "화면", "프론트", "component", "반응형"],
}


def route_agent(question: str) -> str:
    """
    질문 내용 기반 Digital Twin 라우팅

    Args:
        question: 사용자 질문

    Returns:
        선택된 Twin 이름
    """
    q_lower = question.lower()

    for twin_name, keywords in _ROUTING_RULES.items():
        if any(kw in q_lower for kw in keywords):
            return twin_name

    # 기본값: Backend (Jin Park)
    return "Jin Park"


def answer_with_twin(
    twin: TwinAgent,
    org: Dict[str, Any],
    knowledge_snippets: str,
    question: str
) -> str:
    """
    Digital Twin으로 답변 생성 (Mock 모드)

    Args:
        twin: TwinAgent 인스턴스
        org: 조직 설정
        knowledge_snippets: 관련 지식 스니펫
        question: 사용자 질문

    Returns:
        Mock 답변 문자열
    """
    lines = [
        f"[{twin.name} | {twin.role}]",
        f"스타일: {twin.style}",
        "",
        f"질문: {question}",
        "",
        "내가 보는 핵심:",
    ]

    # 지식 스니펫 활용
    if knowledge_snippets:
        lines.append(f"- (회사 지식 참고) {knowledge_snippets[:280]}")

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
