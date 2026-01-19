"""
schemas/response.py - 응답 결과 스키마
SCHEMA-007: AnswerResult, ReviewResult Pydantic 모델
ADR-106: Citation Transparency - 지식 인용 투명성
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .knowledge import KnowledgeItem


class Citation(BaseModel):
    """인용된 지식 항목 (ADR-106)"""
    knowledge_id: str = Field(..., description="지식 항목 ID")
    text: str = Field(..., description="인용된 텍스트")
    source: str = Field(..., description="지식 소스 (meeting_stt, slack_discord 등)")
    tag: str = Field(..., description="지식 태그 (RULE, PITFALL 등)")
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="관련도 점수 (0.0 ~ 1.0)"
    )


class AnswerResult(BaseModel):
    """
    Twin 응답 결과 (ADR-106: Citation Transparency)

    책임: 답변 + 인용 지식 + 라우팅 정보를 하나의 결과로 묶음
    """
    answer: str = Field(..., description="Twin의 답변 텍스트")
    routed_to: str = Field(..., description="라우팅된 Twin 이름")
    citations: List[Citation] = Field(
        default_factory=list,
        description="답변에 사용된 지식 인용 목록"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="응답 생성 시간"
    )

    @property
    def has_citations(self) -> bool:
        """인용된 지식이 있는지 여부"""
        return len(self.citations) > 0


class KeywordMatch(BaseModel):
    """키워드 매칭 결과"""
    keyword: str = Field(..., description="평가 키워드")
    matched: bool = Field(..., description="매칭 여부")
    context: Optional[str] = Field(
        None,
        description="매칭된 컨텍스트 (제출물에서 해당 키워드 주변 텍스트)"
    )


class ReviewResult(BaseModel):
    """
    제출물 리뷰 결과 (ADR-106: Citation Transparency)

    책임: 점수 + 피드백 + 키워드 매칭 근거를 하나의 결과로 묶음
    """
    score: int = Field(..., ge=0, le=100, description="평가 점수 (0-100)")
    strengths: List[str] = Field(default_factory=list, description="강점 목록")
    improvements: List[str] = Field(default_factory=list, description="개선점 목록")
    next_step: str = Field(default="", description="다음 스텝 안내")
    keyword_matches: List[KeywordMatch] = Field(
        default_factory=list,
        description="키워드 매칭 상세 결과"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="리뷰 생성 시간"
    )

    @property
    def matched_count(self) -> int:
        """매칭된 키워드 수"""
        return sum(1 for km in self.keyword_matches if km.matched)

    @property
    def total_keywords(self) -> int:
        """전체 키워드 수"""
        return len(self.keyword_matches)

    @property
    def match_rate(self) -> float:
        """키워드 매칭률 (0.0 ~ 1.0)"""
        if self.total_keywords == 0:
            return 0.0
        return self.matched_count / self.total_keywords
