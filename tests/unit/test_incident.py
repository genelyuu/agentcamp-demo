"""
tests/unit/test_incident.py - Incident 모듈 단위 테스트
TEST-008: Incident Log CRUD 테스트
"""
import pytest
from datetime import datetime

from core.incident import (
    get_all_incidents,
    get_incident,
    create_incident,
    log_incident,
    update_incident_status,
    resolve_incident,
    get_open_incidents,
    get_incidents_by_category,
    get_incidents_by_severity,
    get_incident_summary,
)
from schemas import Incident, RiskCategory, Severity, IncidentStatus


class TestIncidentLoad:
    """Incident 로드 테스트"""

    def test_get_all_returns_list(self):
        """get_all_incidents가 리스트를 반환하는지 테스트"""
        result = get_all_incidents()
        assert isinstance(result, list)

    def test_get_all_returns_incidents(self):
        """get_all_incidents가 Incident 리스트를 반환하는지 테스트"""
        result = get_all_incidents()
        if result:
            assert all(isinstance(i, Incident) for i in result)


class TestIncidentQuery:
    """Incident 조회 테스트"""

    def test_get_incident_nonexistent(self):
        """존재하지 않는 Incident 조회 시 None 반환"""
        result = get_incident("nonexistent-id")
        assert result is None

    def test_get_open_incidents(self):
        """열린 인시던트 조회 테스트"""
        result = get_open_incidents()
        if result:
            assert all(i.status == IncidentStatus.OPEN for i in result)


class TestIncidentCRUD:
    """Incident CRUD 테스트"""

    def test_create_incident(self):
        """Incident 생성 테스트"""
        incident = Incident(
            incident_id="test-inc-001",
            category=RiskCategory.HALLUCINATION,
            severity=Severity.MEDIUM,
            description="테스트용 인시던트입니다.",
            trigger="테스트 트리거"
        )

        result = create_incident(incident)
        assert result is not None

        # 생성 확인
        retrieved = get_incident("test-inc-001")
        assert retrieved is not None
        assert retrieved.description == "테스트용 인시던트입니다."

        # 정리 (직접 삭제 - 내부 API 사용)
        from core.incident import _load_log, _save_log
        log = _load_log()
        log.incidents = [i for i in log.incidents if i.incident_id != "test-inc-001"]
        _save_log(log)

    def test_log_incident(self):
        """log_incident 편의 함수 테스트"""
        result = log_incident(
            category=RiskCategory.BIAS,
            severity=Severity.LOW,
            description="편의 함수로 생성한 인시던트",
            trigger="테스트"
        )

        assert result is not None
        assert result.category == RiskCategory.BIAS
        assert result.severity == Severity.LOW
        assert result.status == IncidentStatus.OPEN

        # 정리
        from core.incident import _load_log, _save_log
        log = _load_log()
        log.incidents = [i for i in log.incidents if i.incident_id != result.incident_id]
        _save_log(log)

    def test_update_incident_status(self):
        """Incident 상태 업데이트 테스트"""
        # 테스트용 인시던트 추가
        incident = Incident(
            incident_id="test-inc-002",
            category=RiskCategory.INJECTION,
            severity=Severity.HIGH,
            description="상태 업데이트 테스트",
            trigger="테스트"
        )
        create_incident(incident)

        # 상태 업데이트
        result = update_incident_status(
            "test-inc-002",
            status=IncidentStatus.INVESTIGATING,
            mitigation="조사 중"
        )
        assert result is not None
        assert result.status == IncidentStatus.INVESTIGATING
        assert result.mitigation == "조사 중"

        # 정리
        from core.incident import _load_log, _save_log
        log = _load_log()
        log.incidents = [i for i in log.incidents if i.incident_id != "test-inc-002"]
        _save_log(log)

    def test_update_incident_nonexistent(self):
        """존재하지 않는 Incident 업데이트 시 None 반환"""
        result = update_incident_status("nonexistent-id", status=IncidentStatus.CLOSED)
        assert result is None

    def test_resolve_incident(self):
        """Incident 해결 테스트"""
        # 테스트용 인시던트 추가
        incident = Incident(
            incident_id="test-inc-003",
            category=RiskCategory.MISROUTE,
            severity=Severity.MEDIUM,
            description="해결 테스트",
            trigger="테스트"
        )
        create_incident(incident)

        # 해결
        result = resolve_incident(
            "test-inc-003",
            mitigation="문제가 해결되었습니다.",
            rca="근본 원인 분석 완료"
        )
        assert result is not None
        assert result.status == IncidentStatus.RESOLVED
        assert result.mitigation == "문제가 해결되었습니다."
        assert result.rca == "근본 원인 분석 완료"
        assert result.resolved_at is not None

        # 정리
        from core.incident import _load_log, _save_log
        log = _load_log()
        log.incidents = [i for i in log.incidents if i.incident_id != "test-inc-003"]
        _save_log(log)

    def test_resolve_incident_nonexistent(self):
        """존재하지 않는 Incident 해결 시 None 반환"""
        result = resolve_incident("nonexistent-id", mitigation="해결")
        assert result is None


class TestIncidentEnums:
    """Incident Enum 테스트"""

    def test_incident_status_values(self):
        """IncidentStatus enum 값 테스트"""
        assert IncidentStatus.OPEN.value == "open"
        assert IncidentStatus.INVESTIGATING.value == "investigating"
        assert IncidentStatus.MITIGATED.value == "mitigated"
        assert IncidentStatus.CLOSED.value == "closed"

    def test_severity_values(self):
        """Severity enum 값 테스트"""
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"


class TestIncidentTimestamps:
    """Incident 타임스탬프 테스트"""

    def test_timestamp_auto_set(self):
        """timestamp가 자동 설정되는지 테스트"""
        incident = Incident(
            incident_id="timestamp-test-001",
            category=RiskCategory.OFFTOPIC,
            severity=Severity.LOW,
            description="타임스탬프 테스트",
            trigger="테스트"
        )

        assert incident.timestamp is not None
        assert isinstance(incident.timestamp, datetime)

    def test_resolved_at_initially_none(self):
        """resolved_at이 초기에 None인지 테스트"""
        incident = Incident(
            incident_id="timestamp-test-002",
            category=RiskCategory.OFFTOPIC,
            severity=Severity.LOW,
            description="타임스탬프 테스트",
            trigger="테스트"
        )

        assert incident.resolved_at is None


class TestIncidentSummary:
    """Incident Summary 테스트"""

    def test_get_incident_summary_structure(self):
        """get_incident_summary 결과 구조 테스트"""
        result = get_incident_summary()

        assert "total" in result
        assert "open" in result
        assert "resolved" in result
        assert "by_severity" in result
        assert "by_category" in result
