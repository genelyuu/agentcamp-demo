"""
schemas/rubric.py - 4칸 구조 평가 스키마
SCORE-001: Checklist, RubricReviewResult Pydantic 모델
ADR-109: Structured Rubric Scoring - 구조화된 평가 기준

SOLID 원칙:
- SRP: 루브릭 평가 관련 스키마만 담당
- OCP: 새로운 평가 항목/칸 추가 시 확장 가능
- DIP: Pydantic 기반 데이터 계약

4칸 구조:
| 원인 분석 (Cause) | 재현 방법 (Reproduction) | 재발 방지 (Prevention) | 증거 (Evidence) |
| 25점            | 25점                    | 25점                  | 25점           |
"""
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================
# 체크리스트 항목 스키마
# ============================================================

class ChecklistItem(BaseModel):
    """개별 체크리스트 항목"""
    id: str = Field(..., description="항목 ID (예: cause_1)")
    label: str = Field(..., description="항목 라벨")
    checked: bool = Field(default=False, description="체크 여부")
    feedback: str = Field(default="", description="해당 항목 피드백")

    @property
    def status_icon(self) -> str:
        """상태 아이콘 반환"""
        return "✅" if self.checked else "❌"


class RubricColumn(BaseModel):
    """
    루브릭 칸 (4칸 중 하나)

    각 칸은 25점 만점이며, 체크리스트 항목들로 구성
    """
    name: Literal["cause", "reproduction", "prevention", "evidence"] = Field(
        ..., description="칸 이름"
    )
    display_name: str = Field(..., description="표시용 이름")
    max_score: int = Field(default=25, description="최대 점수")
    score: int = Field(default=0, ge=0, le=25, description="획득 점수")
    items: List[ChecklistItem] = Field(
        default_factory=list,
        description="체크리스트 항목들"
    )
    summary: str = Field(default="", description="칸 요약 피드백")

    @property
    def completion_rate(self) -> float:
        """체크 완료율 (0.0 ~ 1.0)"""
        if not self.items:
            return 0.0
        checked_count = sum(1 for item in self.items if item.checked)
        return checked_count / len(self.items)

    @property
    def score_percent(self) -> int:
        """점수 퍼센트"""
        return int((self.score / self.max_score) * 100)


# ============================================================
# 기본 체크리스트 정의
# ============================================================

def get_default_cause_items() -> List[ChecklistItem]:
    """원인 분석 체크리스트 기본 항목"""
    return [
        ChecklistItem(id="cause_1", label="문제 현상이 명확히 기술되어 있다"),
        ChecklistItem(id="cause_2", label="근본 원인(root cause)이 식별되어 있다"),
        ChecklistItem(id="cause_3", label="원인과 현상의 인과관계가 논리적이다"),
    ]


def get_default_reproduction_items() -> List[ChecklistItem]:
    """재현 방법 체크리스트 기본 항목"""
    return [
        ChecklistItem(id="repro_1", label="재현 스텝이 순서대로 기술되어 있다"),
        ChecklistItem(id="repro_2", label="재현 환경/조건이 명시되어 있다"),
        ChecklistItem(id="repro_3", label="제3자가 따라할 수 있을 만큼 구체적이다"),
    ]


def get_default_prevention_items() -> List[ChecklistItem]:
    """재발 방지 체크리스트 기본 항목"""
    return [
        ChecklistItem(id="prev_1", label="단기 대응책(hotfix)이 제시되어 있다"),
        ChecklistItem(id="prev_2", label="장기 개선책(permanent fix)이 제시되어 있다"),
        ChecklistItem(id="prev_3", label="모니터링/알림 개선안이 포함되어 있다"),
    ]


def get_default_evidence_items() -> List[ChecklistItem]:
    """증거 체크리스트 기본 항목"""
    return [
        ChecklistItem(id="evid_1", label="로그/스크린샷 등 증거가 첨부되어 있다"),
        ChecklistItem(id="evid_2", label="메트릭/수치 데이터가 인용되어 있다"),
        ChecklistItem(id="evid_3", label="타임라인(언제 발생)이 명시되어 있다"),
    ]


# ============================================================
# 루브릭 평가 결과 스키마
# ============================================================

class RubricReviewResult(BaseModel):
    """
    4칸 구조 루브릭 평가 결과 (ADR-109)

    책임: 4개 칸의 점수 + 체크리스트 + 피드백을 하나의 결과로 묶음
    """
    # 4개 칸
    cause: RubricColumn = Field(..., description="원인 분석 칸")
    reproduction: RubricColumn = Field(..., description="재현 방법 칸")
    prevention: RubricColumn = Field(..., description="재발 방지 칸")
    evidence: RubricColumn = Field(..., description="증거 칸")

    # 메타데이터
    total_score: int = Field(default=0, ge=0, le=100, description="총점 (0-100)")
    grade: Literal["A", "B", "C", "D", "F"] = Field(
        default="F",
        description="등급"
    )
    overall_feedback: str = Field(default="", description="종합 피드백")
    missing_elements: List[str] = Field(
        default_factory=list,
        description="누락된 요소 목록"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="평가 시간"
    )

    @property
    def columns(self) -> List[RubricColumn]:
        """모든 칸 리스트로 반환"""
        return [self.cause, self.reproduction, self.prevention, self.evidence]

    @property
    def all_items(self) -> List[ChecklistItem]:
        """모든 체크리스트 항목 반환"""
        items = []
        for col in self.columns:
            items.extend(col.items)
        return items

    @property
    def checked_count(self) -> int:
        """체크된 항목 수"""
        return sum(1 for item in self.all_items if item.checked)

    @property
    def total_items(self) -> int:
        """전체 항목 수"""
        return len(self.all_items)

    def format_summary(self) -> str:
        """요약 포맷 (UI 표시용)"""
        lines = [
            f"**총점: {self.total_score}/100 ({self.grade})**",
            "",
            "| 칸 | 점수 | 상태 |",
            "|---|---|---|",
        ]

        for col in self.columns:
            status = "✅" if col.score >= 20 else "⚠️" if col.score >= 10 else "❌"
            lines.append(f"| {col.display_name} | {col.score}/25 | {status} |")

        if self.missing_elements:
            lines.append("")
            lines.append("**누락된 요소:**")
            for elem in self.missing_elements[:5]:
                lines.append(f"- {elem}")

        return "\n".join(lines)


# ============================================================
# 팩토리 함수
# ============================================================

def create_empty_rubric_result() -> RubricReviewResult:
    """빈 루브릭 평가 결과 생성"""
    return RubricReviewResult(
        cause=RubricColumn(
            name="cause",
            display_name="원인 분석",
            items=get_default_cause_items()
        ),
        reproduction=RubricColumn(
            name="reproduction",
            display_name="재현 방법",
            items=get_default_reproduction_items()
        ),
        prevention=RubricColumn(
            name="prevention",
            display_name="재발 방지",
            items=get_default_prevention_items()
        ),
        evidence=RubricColumn(
            name="evidence",
            display_name="증거",
            items=get_default_evidence_items()
        ),
        total_score=0,
        grade="F",
        overall_feedback="",
        missing_elements=[]
    )


def calculate_grade(score: int) -> Literal["A", "B", "C", "D", "F"]:
    """점수에 따른 등급 계산"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
