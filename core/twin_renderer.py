"""
core/twin_renderer.py - 트윈별 강제 산출물 스키마 렌더러
ROUTE-003: render_*_answer() 트윈별 렌더러 구현
ADR-108: Explainable Routing - 구조화된 응답 포맷

SOLID 원칙:
- SRP: 응답 렌더링만 담당 (LLM 호출/라우팅과 분리)
- OCP: 새 트윈/포맷 추가 시 확장 가능
- DIP: TwinAgent 인터페이스에 의존
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents import TwinAgent


@dataclass
class StructuredSection:
    """구조화된 섹션 (ADR-108)"""
    title: str
    content: str
    items: List[str] = field(default_factory=list)
    is_checklist: bool = False


@dataclass
class StructuredAnswer:
    """
    구조화된 답변 결과 (ADR-108)

    책임: 트윈별 고유 섹션 구조를 강제하여 차별화된 산출물 생성
    """
    twin_name: str
    role: str
    emoji: str
    greeting: str
    sections: List[StructuredSection]
    closing: str
    raw_answer: str  # 원본 LLM 응답 보존

    def to_markdown(self) -> str:
        """마크다운 형식으로 변환"""
        lines = []

        # 헤더
        if self.greeting:
            lines.append(f"{self.emoji} **{self.greeting}**")
            lines.append("")

        # 섹션
        for section in self.sections:
            lines.append(f"### {section.title}")
            if section.is_checklist and section.items:
                for item in section.items:
                    lines.append(f"- [ ] {item}")
            elif section.items:
                for item in section.items:
                    lines.append(f"- {item}")
            elif section.content:
                lines.append(section.content)
            lines.append("")

        # 클로징
        if self.closing:
            lines.append(f"---")
            lines.append(f"*{self.closing}*")

        return "\n".join(lines)


def _parse_answer_to_sections(answer: str) -> List[str]:
    """
    LLM 응답을 섹션 단위로 파싱

    - 줄바꿈 또는 문장 단위로 분리
    - 빈 줄/공백 제거
    """
    lines = [line.strip() for line in answer.split('\n') if line.strip()]
    return lines


def _extract_bullet_items(text: str) -> List[str]:
    """불릿 포인트 추출 (-로 시작하는 항목)"""
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            items.append(line[1:].strip())
    return items


# ============================================================
# CEO (Sam Lee) 렌더러 - 결론 중심, 의사결정 구조
# ============================================================

def render_ceo_answer(twin: TwinAgent, raw_answer: str) -> StructuredAnswer:
    """
    CEO 트윈 응답 렌더러 (ADR-108)

    강제 산출물 구조:
    - 결론 (Decision Summary)
    - 선택지 (Options)
    - 트레이드오프 (Trade-off)
    - Go/No-Go 판단
    - 다음 액션
    """
    response_format = twin.response_format
    lines = _parse_answer_to_sections(raw_answer)

    # 간단한 휴리스틱으로 섹션 분배
    sections = []

    # 결론 섹션
    conclusion = lines[0] if lines else "판단이 필요합니다."
    sections.append(StructuredSection(
        title="결론",
        content=conclusion,
        items=[],
        is_checklist=False
    ))

    # 근거 섹션 (중간 내용)
    if len(lines) > 2:
        rationale = lines[1:-1]
        sections.append(StructuredSection(
            title="근거",
            content="",
            items=rationale[:3],  # 최대 3개
            is_checklist=False
        ))

    # 리스크/트레이드오프 섹션
    sections.append(StructuredSection(
        title="리스크 & 트레이드오프",
        content="",
        items=["비용 vs 속도", "품질 vs 일정"],
        is_checklist=False
    ))

    # 다음 액션
    next_action = lines[-1] if lines else "다음 스텝을 정해주세요."
    sections.append(StructuredSection(
        title="다음 액션",
        content=next_action,
        items=[],
        is_checklist=False
    ))

    return StructuredAnswer(
        twin_name=twin.name,
        role=twin.role,
        emoji=response_format.emoji if response_format else "🎯",
        greeting=response_format.greeting if response_format else "",
        sections=sections,
        closing=response_format.closing if response_format else "빠르게 움직이세요.",
        raw_answer=raw_answer
    )


# ============================================================
# PM (JH Kim) 렌더러 - 체크리스트/성공조건 구조
# ============================================================

def render_pm_answer(twin: TwinAgent, raw_answer: str) -> StructuredAnswer:
    """
    PM 트윈 응답 렌더러 (ADR-108)

    강제 산출물 구조:
    - 문제 정의 (Problem Statement)
    - 가설 (Hypotheses)
    - 성공 조건 (Acceptance Criteria)
    - 실험 계획 (Experiment Plan)
    - 열린 질문 (Open Questions)
    """
    response_format = twin.response_format
    lines = _parse_answer_to_sections(raw_answer)

    sections = []

    # 문제 정의
    problem = lines[0] if lines else "문제를 정의해야 합니다."
    sections.append(StructuredSection(
        title="문제 정의",
        content=problem,
        items=[],
        is_checklist=False
    ))

    # 가설
    sections.append(StructuredSection(
        title="가설",
        content="",
        items=["가설 1: [원인] → [결과]", "가설 2: [조건] → [예상 결과]"],
        is_checklist=False
    ))

    # 성공 조건 (체크리스트)
    ac_items = []
    if len(lines) > 1:
        ac_items = [f"AC: {line}" for line in lines[1:3]]
    if not ac_items:
        ac_items = ["AC1: 기능이 동작한다", "AC2: 에러가 없다"]
    sections.append(StructuredSection(
        title="성공 조건 (AC)",
        content="",
        items=ac_items,
        is_checklist=True
    ))

    # 우선순위/스코프
    sections.append(StructuredSection(
        title="우선순위",
        content="",
        items=["P0: 필수", "P1: 권장", "P2: 선택"],
        is_checklist=False
    ))

    return StructuredAnswer(
        twin_name=twin.name,
        role=twin.role,
        emoji=response_format.emoji if response_format else "📋",
        greeting=response_format.greeting if response_format else "좋은 질문이에요.",
        sections=sections,
        closing=response_format.closing if response_format else "하나씩 체크해보세요!",
        raw_answer=raw_answer
    )


# ============================================================
# Frontend (Seul Kim) 렌더러 - UX/에러케이스 구조
# ============================================================

def render_frontend_answer(twin: TwinAgent, raw_answer: str) -> StructuredAnswer:
    """
    Frontend 트윈 응답 렌더러 (ADR-108)

    강제 산출물 구조:
    - 사용자 흐름 (User Flow)
    - 에러 케이스 (Edge Cases)
    - 최소 UI 변경 (Minimal UI Change)
    - 카피 가이드라인 (Copy Guideline)
    - QA 체크리스트
    """
    response_format = twin.response_format
    lines = _parse_answer_to_sections(raw_answer)

    sections = []

    # 사용자 흐름
    flow = lines[0] if lines else "사용자 흐름을 정의해야 합니다."
    sections.append(StructuredSection(
        title="사용자 흐름",
        content=flow,
        items=[],
        is_checklist=False
    ))

    # 에러 케이스
    sections.append(StructuredSection(
        title="에러 케이스",
        content="",
        items=["입력값 없음", "네트워크 에러", "권한 부족", "타임아웃"],
        is_checklist=True
    ))

    # 구현 포인트
    impl_items = lines[1:3] if len(lines) > 1 else ["컴포넌트 분리", "상태 관리"]
    sections.append(StructuredSection(
        title="구현 포인트",
        content="",
        items=impl_items,
        is_checklist=False
    ))

    # 개선 제안
    sections.append(StructuredSection(
        title="개선 제안",
        content=lines[-1] if lines else "UX 개선점을 검토하세요.",
        items=[],
        is_checklist=False
    ))

    return StructuredAnswer(
        twin_name=twin.name,
        role=twin.role,
        emoji=response_format.emoji if response_format else "🎨",
        greeting=response_format.greeting if response_format else "UX 관점에서 보면요~",
        sections=sections,
        closing=response_format.closing if response_format else "사용자 입장에서 테스트해보세요!",
        raw_answer=raw_answer
    )


# ============================================================
# Backend (Jin Park) 렌더러 - 증거/재현/원인 구조
# ============================================================

def render_backend_answer(twin: TwinAgent, raw_answer: str) -> StructuredAnswer:
    """
    Backend 트윈 응답 렌더러 (ADR-108)

    강제 산출물 구조:
    - 증거 체크리스트 (Evidence Checklist)
    - 재현 스텝 (Reproduction Steps)
    - 원인 후보 (Root-cause Candidates)
    - 대응 방안 (Mitigation Plan)
    - 계측 포인트 (Instrumentation)
    """
    response_format = twin.response_format
    lines = _parse_answer_to_sections(raw_answer)

    sections = []

    # 현상 분석
    symptom = lines[0] if lines else "현상을 분석해야 합니다."
    sections.append(StructuredSection(
        title="현상 분석",
        content=symptom,
        items=[],
        is_checklist=False
    ))

    # 원인 가설
    sections.append(StructuredSection(
        title="원인 가설",
        content="",
        items=["가설 1: [시스템 컴포넌트] 문제", "가설 2: [외부 의존성] 문제"],
        is_checklist=False
    ))

    # 검증 방법 (체크리스트)
    sections.append(StructuredSection(
        title="검증 방법",
        content="",
        items=["로그 확인", "메트릭 확인", "재현 테스트", "프로파일링"],
        is_checklist=True
    ))

    # 해결 방안
    solution = lines[-1] if lines else "해결 방안을 검토하세요."
    sections.append(StructuredSection(
        title="해결 방안",
        content=solution,
        items=[],
        is_checklist=False
    ))

    return StructuredAnswer(
        twin_name=twin.name,
        role=twin.role,
        emoji=response_format.emoji if response_format else "🔧",
        greeting=response_format.greeting if response_format else "",
        sections=sections,
        closing=response_format.closing if response_format else "로그와 메트릭으로 확인하세요.",
        raw_answer=raw_answer
    )


# ============================================================
# 통합 렌더러 디스패처
# ============================================================

# 트윈 이름 → 렌더러 매핑
_RENDERER_MAP = {
    "Sam Lee": render_ceo_answer,
    "JH Kim": render_pm_answer,
    "Seul Kim": render_frontend_answer,
    "Jin Park": render_backend_answer,
}


def render_twin_answer(twin: TwinAgent, raw_answer: str) -> StructuredAnswer:
    """
    트윈별 구조화된 응답 렌더링 (ADR-108)

    Args:
        twin: TwinAgent 인스턴스
        raw_answer: LLM이 생성한 원본 응답

    Returns:
        StructuredAnswer: 트윈별 강제 스키마가 적용된 구조화된 응답
    """
    renderer = _RENDERER_MAP.get(twin.name, render_backend_answer)
    return renderer(twin, raw_answer)


def get_available_renderers() -> List[str]:
    """사용 가능한 렌더러 목록 반환"""
    return list(_RENDERER_MAP.keys())
