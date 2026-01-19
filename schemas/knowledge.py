"""
schemas/knowledge.py - 지식 항목 스키마
SCHEMA-002: KnowledgeItem Pydantic 모델
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .enums import KnowledgeTag, KnowledgeSource


class KnowledgeItem(BaseModel):
    """지식 항목 스키마 (SCHEMA-002)"""
    id: str = Field(..., description="고유 ID")
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="지식 내용"
    )
    tag: KnowledgeTag = Field(..., description="지식 태그")
    source: KnowledgeSource = Field(..., description="지식 소스")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="생성 시간"
    )

    class Config:
        use_enum_values = True


class KnowledgeBase(BaseModel):
    """지식 베이스 컨테이너"""
    items: list[KnowledgeItem] = Field(default_factory=list)
