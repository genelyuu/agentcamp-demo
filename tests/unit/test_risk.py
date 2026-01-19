"""
tests/unit/test_risk.py - Risk 모듈 단위 테스트
TEST-007: Risk Register CRUD 테스트
"""
import pytest
from datetime import datetime

from core.risk import (
    get_all_risks,
    get_risk,
    create_risk,
    update_risk,
    delete_risk,
    get_risks_by_category,
    get_risks_by_status,
    get_high_risks,
    get_risk_summary,
)
from schemas import RiskEntry, RiskCategory


class TestRiskLoad:
    """Risk Register 로드 테스트"""

    def test_get_all_returns_list(self):
        """get_all_risks가 리스트를 반환하는지 테스트"""
        result = get_all_risks()
        assert isinstance(result, list)

    def test_get_all_returns_risk_entries(self):
        """get_all_risks가 RiskEntry 리스트를 반환하는지 테스트"""
        result = get_all_risks()
        if result:
            assert all(isinstance(r, RiskEntry) for r in result)


class TestRiskQuery:
    """Risk 조회 테스트"""

    def test_get_risk_by_id(self):
        """ID로 Risk 조회 테스트"""
        risks = get_all_risks()
        if risks:
            risk_id = risks[0].risk_id
            result = get_risk(risk_id)
            assert result is not None
            assert result.risk_id == risk_id

    def test_get_risk_nonexistent(self):
        """존재하지 않는 Risk 조회 시 None 반환"""
        result = get_risk("nonexistent-id")
        assert result is None

    def test_get_risks_by_category(self):
        """카테고리별 필터링 테스트"""
        result = get_risks_by_category(RiskCategory.HALLUCINATION)
        if result:
            assert all(r.category == RiskCategory.HALLUCINATION for r in result)

    def test_get_risks_by_status(self):
        """상태별 필터링 테스트"""
        result = get_risks_by_status("open")
        if result:
            assert all(r.status == "open" for r in result)

    def test_get_high_risks(self):
        """높은 리스크 조회 테스트"""
        result = get_high_risks(threshold=12)
        if result:
            assert all(r.risk_score >= 12 for r in result)


class TestRiskCRUD:
    """Risk CRUD 테스트"""

    def test_create_risk(self):
        """Risk 생성 테스트"""
        new_risk = RiskEntry(
            risk_id="test-risk-001",
            category=RiskCategory.HALLUCINATION,
            description="테스트용 리스크입니다.",
            likelihood=3,
            impact=4,
            controls=["테스트 완화 조치"],
            owner="테스터"
        )

        result = create_risk(new_risk)
        assert result is not None

        # 생성 확인
        retrieved = get_risk("test-risk-001")
        assert retrieved is not None
        assert retrieved.description == "테스트용 리스크입니다."

        # 정리
        delete_risk("test-risk-001")

    def test_update_risk(self):
        """Risk 수정 테스트"""
        # 테스트용 Risk 추가
        new_risk = RiskEntry(
            risk_id="test-risk-002",
            category=RiskCategory.BIAS,
            description="수정 전 설명",
            likelihood=2,
            impact=3,
            controls=[],
            owner="테스터"
        )
        create_risk(new_risk)

        # 수정
        result = update_risk("test-risk-002", {"description": "수정 후 설명", "likelihood": 4})
        assert result is not None
        assert result.description == "수정 후 설명"
        assert result.likelihood == 4

        # 정리
        delete_risk("test-risk-002")

    def test_update_risk_nonexistent(self):
        """존재하지 않는 Risk 수정 시 None 반환"""
        result = update_risk("nonexistent-id", {"description": "새 설명"})
        assert result is None

    def test_delete_risk(self):
        """Risk 삭제 테스트"""
        # 테스트용 Risk 추가
        new_risk = RiskEntry(
            risk_id="test-risk-003",
            category=RiskCategory.PII_LEAK,
            description="삭제 테스트",
            likelihood=1,
            impact=2,
            controls=[],
            owner="테스터"
        )
        create_risk(new_risk)

        # 삭제
        result = delete_risk("test-risk-003")
        assert result is True

        # 삭제 확인
        retrieved = get_risk("test-risk-003")
        assert retrieved is None

    def test_delete_risk_nonexistent(self):
        """존재하지 않는 Risk 삭제 시 False 반환"""
        result = delete_risk("nonexistent-id")
        assert result is False


class TestRiskScore:
    """Risk Score 계산 테스트"""

    def test_risk_score_calculation(self):
        """risk_score가 likelihood * impact로 계산되는지 테스트"""
        risk = RiskEntry(
            risk_id="score-test",
            category=RiskCategory.HALLUCINATION,
            description="점수 테스트",
            likelihood=3,
            impact=4,
            controls=[],
            owner="테스터"
        )

        assert risk.risk_score == 12  # 3 * 4

    def test_risk_level_low(self):
        """낮은 위험 수준 테스트"""
        risk = RiskEntry(
            risk_id="level-test-low",
            category=RiskCategory.HALLUCINATION,
            description="낮은 위험",
            likelihood=1,
            impact=2,
            controls=[],
            owner="테스터"
        )

        assert risk.risk_level == "low"  # 1 * 2 = 2 < 6

    def test_risk_level_medium(self):
        """중간 위험 수준 테스트"""
        risk = RiskEntry(
            risk_id="level-test-medium",
            category=RiskCategory.HALLUCINATION,
            description="중간 위험",
            likelihood=2,
            impact=4,
            controls=[],
            owner="테스터"
        )

        assert risk.risk_level == "medium"  # 2 * 4 = 8, 6 <= 8 < 12

    def test_risk_level_high(self):
        """높은 위험 수준 테스트"""
        risk = RiskEntry(
            risk_id="level-test-high",
            category=RiskCategory.HALLUCINATION,
            description="높은 위험",
            likelihood=3,
            impact=5,
            controls=[],
            owner="테스터"
        )

        assert risk.risk_level == "high"  # 3 * 5 = 15, 12 <= 15 < 20

    def test_risk_level_critical(self):
        """심각한 위험 수준 테스트"""
        risk = RiskEntry(
            risk_id="level-test-critical",
            category=RiskCategory.HALLUCINATION,
            description="심각한 위험",
            likelihood=5,
            impact=5,
            controls=[],
            owner="테스터"
        )

        assert risk.risk_level == "critical"  # 5 * 5 = 25 >= 20


class TestRiskSummary:
    """Risk Summary 테스트"""

    def test_get_risk_summary_structure(self):
        """get_risk_summary 결과 구조 테스트"""
        result = get_risk_summary()

        assert "total" in result
        assert "by_status" in result
        assert "by_level" in result
        assert "avg_score" in result
        assert "high_risk_count" in result
