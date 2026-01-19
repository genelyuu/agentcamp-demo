"""
schemas/organization.py - 조직 설정 스키마
SCHEMA-003: OrgConfig Pydantic 모델
"""
from typing import Optional
from pydantic import BaseModel, Field


class RubricConfig(BaseModel):
    """평가 루브릭 설정"""
    acceptance_keywords: list[str] = Field(
        default_factory=lambda: ["원인", "재현", "재발방지", "로그"],
        description="완료 기준 키워드"
    )


class OrgConfig(BaseModel):
    """조직 설정 스키마 (SCHEMA-003)"""
    company: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="회사명"
    )
    role: str = Field(
        default="Backend Engineer",
        description="OJT 직무"
    )
    tools: list[str] = Field(
        default_factory=lambda: ["Slack", "GitHub"],
        description="사용 도구 목록"
    )
    rubric: RubricConfig = Field(
        default_factory=RubricConfig,
        description="평가 루브릭"
    )

    class Config:
        validate_assignment = True
