"""
schemas/session.py - 사용자 세션 스키마
SCHEMA-004: UserSession Pydantic 모델
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """대화 메시지"""
    role: str = Field(..., description="sender role: user/assistant/twin")
    content: str = Field(..., description="메시지 내용")
    twin_name: Optional[str] = Field(None, description="응답한 Twin 이름")
    timestamp: Optional[str] = Field(None, description="메시지 시간")


class OJTTask(BaseModel):
    """OJT 미션"""
    title: str = Field(..., description="미션 제목")
    context: str = Field(..., description="상황 설명")
    deliverable: str = Field(..., description="제출물 요구사항")
    acceptance_keywords: list[str] = Field(
        default_factory=list,
        description="완료 기준 키워드"
    )


class UserSession(BaseModel):
    """사용자 세션 스키마 (SCHEMA-004)"""
    user_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., description="사용자 표시명")
    adapt_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="적응도 점수 (0-100)"
    )
    risk_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="리스크 점수 (0-100)"
    )
    tasks_done: int = Field(default=0, ge=0, description="완료한 업무 수")
    questions: int = Field(default=0, ge=0, description="질문 횟수")
    last_task: Optional[OJTTask] = Field(None, description="마지막 미션")
    chat_history: list[ChatMessage] = Field(
        default_factory=list,
        description="대화 기록"
    )

    @field_validator('adapt_score', 'risk_score', mode='before')
    @classmethod
    def clamp_score(cls, v: float) -> float:
        """점수를 0-100 범위로 클램핑 (ge/le 검증 전 실행)"""
        if v is None:
            return 50.0
        return max(0.0, min(100.0, float(v)))


class SessionStore(BaseModel):
    """세션 저장소"""
    users: dict[str, UserSession] = Field(default_factory=dict)
