"""
schemas/audit.py - 감사 로그 스키마
SCHEMA-005: AuditEvent Pydantic 모델
"""
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """감사 이벤트 스키마 (SCHEMA-005)"""
    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="이벤트 고유 ID"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="발생 시간"
    )
    event_type: str = Field(
        ...,
        description="이벤트 유형: question, submission, ingestion, error"
    )
    user_id: Optional[str] = Field(None, description="사용자 ID")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="이벤트 페이로드"
    )
    result: str = Field(
        ...,
        description="결과: success, fail, blocked"
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="요청 추적 ID"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
