"""
schemas/risk.py - 리스크 관리 스키마
RISK-003, RISK-004: RiskEntry & Incident Pydantic 모델
ADR-105: Risk Register
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field, computed_field

from .enums import RiskCategory, Severity, IncidentStatus


class RiskEntry(BaseModel):
    """
    리스크 항목 스키마 (RISK-003)

    likelihood × impact = risk_score
    """
    risk_id: str = Field(
        default_factory=lambda: f"R-{uuid4().hex[:6].upper()}",
        description="리스크 ID"
    )
    category: RiskCategory = Field(..., description="리스크 카테고리")
    description: str = Field(..., min_length=1, max_length=500, description="리스크 설명")
    likelihood: int = Field(
        ...,
        ge=1,
        le=5,
        description="발생 가능성 (1-5)"
    )
    impact: int = Field(
        ...,
        ge=1,
        le=5,
        description="영향도 (1-5)"
    )
    controls: List[str] = Field(
        default_factory=list,
        description="완화 조치 목록"
    )
    owner: str = Field(..., description="담당자")
    status: str = Field(
        default="open",
        description="상태: open, mitigated, closed, accepted"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="수정 시간"
    )

    @computed_field
    @property
    def risk_score(self) -> int:
        """리스크 점수 (likelihood × impact)"""
        return self.likelihood * self.impact

    @computed_field
    @property
    def risk_level(self) -> str:
        """리스크 레벨 (score 기반)"""
        score = self.risk_score
        if score >= 20:
            return "critical"
        elif score >= 12:
            return "high"
        elif score >= 6:
            return "medium"
        else:
            return "low"

    class Config:
        use_enum_values = True


class Incident(BaseModel):
    """
    인시던트 스키마 (RISK-004)
    """
    incident_id: str = Field(
        default_factory=lambda: f"INC-{uuid4().hex[:6].upper()}",
        description="인시던트 ID"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="발생 시간"
    )
    category: RiskCategory = Field(..., description="리스크 카테고리")
    severity: Severity = Field(..., description="심각도")
    description: str = Field(..., min_length=1, max_length=1000, description="인시던트 설명")
    trigger: str = Field(..., description="트리거/원인")
    status: IncidentStatus = Field(
        default=IncidentStatus.OPEN,
        description="인시던트 상태"
    )
    mitigation: Optional[str] = Field(None, description="완화 조치")
    rca: Optional[str] = Field(None, description="근본 원인 분석 (Root Cause Analysis)")
    related_risk_id: Optional[str] = Field(None, description="관련 리스크 ID")
    resolved_at: Optional[datetime] = Field(None, description="해결 시간")

    class Config:
        use_enum_values = True


class RiskRegister(BaseModel):
    """리스크 레지스터 컨테이너"""
    risks: List[RiskEntry] = Field(default_factory=list)


class IncidentLog(BaseModel):
    """인시던트 로그 컨테이너"""
    incidents: List[Incident] = Field(default_factory=list)
