"""
core/llm/mock.py - Mock Capability 구현
CAP-006: Capability별 Mock 구현
ADR-104: LLM Capability Interface
LOG-004: 로깅 적용
"""
from typing import Any, Dict, List
from uuid import uuid4
from datetime import datetime

from agents import TwinAgent
from schemas import KnowledgeItem, KnowledgeTag, KnowledgeSource, OJTTask
from core.logger import get_logger

logger = get_logger("llm.mock")


# 라우팅 키워드 규칙
_ROUTING_RULES: Dict[str, List[str]] = {
    "Sam Lee": ["우선순위", "전략", "고객", "리스크", "비용"],
    "JH Kim": ["요구사항", "스코프", "정의", "kpi", "지표"],
    "Seul Kim": ["ui", "ux", "화면", "프론트", "component", "반응형"],
}


class MockRouter:
    """Mock 라우팅 Capability - 키워드 기반"""

    def route(self, question: str) -> str:
        """키워드 매칭으로 Twin 선택"""
        q_lower = question.lower()

        for twin_name, keywords in _ROUTING_RULES.items():
            if any(kw in q_lower for kw in keywords):
                logger.debug(f"MockRouter routed to {twin_name}: question='{question[:50]}...'")
                return twin_name

        # 기본값: Backend (Jin Park)
        logger.debug(f"MockRouter default to Jin Park: question='{question[:50]}...'")
        return "Jin Park"


class MockAnswerer:
    """Mock 응답 Capability - 템플릿 기반"""

    def answer(
        self,
        twin: TwinAgent,
        org: Dict[str, Any],
        knowledge: str,
        question: str
    ) -> str:
        """템플릿 기반 응답 생성"""
        logger.debug(f"MockAnswerer generating: twin={twin.name}, question_len={len(question)}")
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


class MockExtractor:
    """Mock 추출 Capability - 규칙 기반"""

    # 태그 키워드 매핑
    _TAG_KEYWORDS = {
        KnowledgeTag.RULE: ["규칙", "원칙", "반드시", "금지", "필수"],
        KnowledgeTag.PITFALL: ["주의", "실수", "함정", "조심", "위험"],
        KnowledgeTag.GLOSSARY: ["정의", "뜻", "의미", "용어", "약어"],
        KnowledgeTag.PROCESS: ["순서", "절차", "단계", "프로세스", "워크플로우"],
    }

    def extract(self, source: str, text: str) -> List[KnowledgeItem]:
        """규칙 기반 지식 추출"""
        logger.debug(f"MockExtractor extracting: source={source}, text_len={len(text)}")
        items = []

        # 소스 타입 변환
        try:
            source_enum = KnowledgeSource(source)
        except ValueError:
            source_enum = KnowledgeSource.MEETING_STT

        # 문장 단위 분리
        sentences = [s.strip() for s in text.replace("\n", ".").split(".") if s.strip()]

        for sentence in sentences:
            if len(sentence) < 10:
                continue

            # 태그 결정
            tag = self._determine_tag(sentence)

            items.append(KnowledgeItem(
                id=f"k-{uuid4().hex[:8]}",
                text=sentence[:1000],
                tag=tag,
                source=source_enum,
                created_at=datetime.utcnow()
            ))

        logger.debug(f"MockExtractor extracted {len(items)} items")
        return items

    def _determine_tag(self, text: str) -> KnowledgeTag:
        """텍스트 기반 태그 결정"""
        text_lower = text.lower()

        for tag, keywords in self._TAG_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return tag

        return KnowledgeTag.PROCESS


class MockJudge:
    """Mock 평가 Capability - 키워드 기반"""

    def judge(self, task: OJTTask, submission: str) -> Dict[str, Any]:
        """키워드 기반 평가"""
        logger.debug(f"MockJudge evaluating: task={task.title}, submission_len={len(submission)}")
        score = 50
        feedback: Dict[str, Any] = {
            "score": 0,
            "strengths": [],
            "improvements": [],
            "next_step": ""
        }

        # 키워드 매칭
        keywords = task.acceptance_keywords
        hit_count = self._count_keyword_hits(keywords, submission)

        # 점수 계산
        if keywords:
            keyword_score = int(50 * (hit_count / len(keywords)))
            score += keyword_score
        else:
            score += 20

        # 강점 평가
        threshold = max(1, len(keywords) // 2)
        if hit_count >= threshold:
            feedback["strengths"].append("핵심 포인트를 일부 포함했습니다.")

        # 개선점 평가
        if len(submission) < 120:
            feedback["improvements"].append(
                "설명이 너무 짧습니다. 근거(로그/수치/재현 조건)를 추가하세요."
            )

        if not feedback["strengths"]:
            feedback["improvements"].append(
                "완료 기준 키워드(원인/재발방지/재현조건 등)를 더 명시하세요."
            )

        # 다음 스텝
        feedback["next_step"] = (
            "리뷰 반영 후 1회 재제출하거나, "
            "AI 멘토에게 '어떤 로그를 봐야 하나'를 질문해보세요."
        )

        feedback["score"] = min(100, score)
        logger.debug(f"MockJudge result: score={feedback['score']}")
        return feedback

    def _count_keyword_hits(self, keywords: List[str], submission: str) -> int:
        """키워드 포함 횟수 계산"""
        lower_submission = submission.lower()
        return sum(1 for kw in keywords if kw.lower() in lower_submission)
