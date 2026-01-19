"""
schemas/routing.py - 설명가능 라우팅 스키마
SCHEMA-008: Candidate, RoutingResult Pydantic 모델
ADR-108: Explainable Routing - 라우팅 투명성

SOLID 원칙:
- SRP: 라우팅 관련 스키마만 담당
- OCP: 새로운 라우팅 메타데이터 추가 시 확장 가능
"""
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """라우팅 후보 트윈 (ADR-108)"""
    name: str = Field(..., description="트윈 이름")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="적합도 점수 (0.0 ~ 1.0)"
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="매칭된 키워드 목록"
    )

    @property
    def confidence_percent(self) -> int:
        """신뢰도를 퍼센트로 반환"""
        return int(self.score * 100)


class RoutingResult(BaseModel):
    """
    설명가능 라우팅 결과 (ADR-108: Explainable Routing)

    책임: 라우팅 결정 + 근거 + 대안 후보를 하나의 결과로 묶음
    """
    selected: str = Field(..., description="선택된 트윈 이름")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="선택된 트윈의 적합도 점수"
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="선택 근거가 된 키워드 목록"
    )
    candidates: List[Candidate] = Field(
        default_factory=list,
        description="상위 후보 목록 (점수 내림차순)"
    )
    reason: str = Field(
        default="",
        description="사람이 읽을 수 있는 라우팅 근거 설명"
    )
    mode: Literal["auto", "manual"] = Field(
        default="auto",
        description="라우팅 모드 (auto: 자동, manual: 수동 지정)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="라우팅 시간"
    )

    @property
    def confidence_percent(self) -> int:
        """신뢰도를 퍼센트로 반환"""
        return int(self.score * 100)

    @property
    def has_alternatives(self) -> bool:
        """대안 후보가 있는지 여부"""
        return len(self.candidates) > 1

    @property
    def alternatives(self) -> List[Candidate]:
        """선택된 트윈 외의 대안 후보들"""
        return [c for c in self.candidates if c.name != self.selected]

    def format_reason_display(self) -> str:
        """UI 표시용 라우팅 근거 포맷"""
        parts = []

        # 매칭 키워드
        if self.matched_keywords:
            kw_str = ", ".join(self.matched_keywords[:5])
            parts.append(f"매칭 키워드: {kw_str}")

        # 신뢰도
        parts.append(f"신뢰도: {self.confidence_percent}%")

        # 대안
        alts = self.alternatives
        if alts:
            alt_str = ", ".join([f"{c.name}({c.confidence_percent}%)" for c in alts[:2]])
            parts.append(f"대안: {alt_str}")

        return " | ".join(parts)
