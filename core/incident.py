"""
core/incident.py - 인시던트 로그 CRUD API
RISK-007: Incident Log CRUD API
ADR-105: Risk Register
DUP-002: BaseJSONRepository 활용
"""
import os
from typing import List, Optional
from datetime import datetime

from schemas import Incident, IncidentLog, IncidentStatus, RiskCategory, Severity
from .repository import BaseJSONRepository

# 파일 경로
INCIDENT_PATH = os.path.join("data", "incidents.json")

# Repository 인스턴스 (내부 구현)
_repo = BaseJSONRepository[Incident](
    path=INCIDENT_PATH,
    container_cls=IncidentLog,
    item_key="incidents"
)


# ============================================================
# Legacy Functions (Facade) - 외부 API 호환성 유지
# ============================================================

def _ensure_file() -> None:
    """파일 존재 확인 및 생성 (Legacy 호환)"""
    _repo._ensure_file()


def _load_log() -> IncidentLog:
    """인시던트 로그 로드 (Legacy 호환)"""
    return _repo._load()


def _save_log(log: IncidentLog) -> None:
    """인시던트 로그 저장 (Legacy 호환)"""
    _repo._save(log)


# ============================================================
# CRUD Operations
# ============================================================

def get_all_incidents() -> List[Incident]:
    """모든 인시던트 조회"""
    return _repo.get_all()


def get_incident(incident_id: str) -> Optional[Incident]:
    """특정 인시던트 조회"""
    return _repo.get_by_id(incident_id, id_field="incident_id")


def create_incident(incident: Incident) -> Incident:
    """인시던트 생성"""
    return _repo.create(incident)


def log_incident(
    category: RiskCategory,
    severity: Severity,
    description: str,
    trigger: str,
    related_risk_id: Optional[str] = None
) -> Incident:
    """간편 인시던트 로깅"""
    incident = Incident(
        category=category,
        severity=severity,
        description=description,
        trigger=trigger,
        status=IncidentStatus.OPEN,
        related_risk_id=related_risk_id
    )
    return create_incident(incident)


def update_incident_status(
    incident_id: str,
    status: IncidentStatus,
    mitigation: Optional[str] = None,
    rca: Optional[str] = None
) -> Optional[Incident]:
    """인시던트 상태 변경"""
    updates = {"status": status}

    if mitigation:
        updates["mitigation"] = mitigation
    if rca:
        updates["rca"] = rca

    if status == IncidentStatus.RESOLVED:
        updates["resolved_at"] = datetime.utcnow().isoformat()

    return _repo.update(
        item_id=incident_id,
        updates=updates,
        id_field="incident_id",
        item_cls=Incident
    )


def resolve_incident(
    incident_id: str,
    mitigation: str,
    rca: Optional[str] = None
) -> Optional[Incident]:
    """인시던트 해결 처리"""
    return update_incident_status(
        incident_id=incident_id,
        status=IncidentStatus.RESOLVED,
        mitigation=mitigation,
        rca=rca
    )


# ============================================================
# Query Operations
# ============================================================

def get_open_incidents() -> List[Incident]:
    """열린 인시던트 조회"""
    return _repo.filter(lambda i: i.status == IncidentStatus.OPEN)


def get_incidents_by_category(category: RiskCategory) -> List[Incident]:
    """카테고리별 인시던트 조회"""
    return _repo.filter(lambda i: i.category == category)


def get_incidents_by_severity(severity: Severity) -> List[Incident]:
    """심각도별 인시던트 조회"""
    return _repo.filter(lambda i: i.severity == severity)


def get_incident_summary() -> dict:
    """인시던트 요약 통계"""
    incidents = get_all_incidents()

    if not incidents:
        return {
            "total": 0,
            "open": 0,
            "resolved": 0,
            "by_severity": {},
            "by_category": {}
        }

    open_count = _repo.count(lambda i: i.status == IncidentStatus.OPEN)
    resolved_count = _repo.count(lambda i: i.status == IncidentStatus.RESOLVED)

    by_severity = {}
    by_category = {}

    for incident in incidents:
        sev = incident.severity
        by_severity[sev] = by_severity.get(sev, 0) + 1

        cat = incident.category
        by_category[cat] = by_category.get(cat, 0) + 1

    return {
        "total": len(incidents),
        "open": open_count,
        "resolved": resolved_count,
        "by_severity": by_severity,
        "by_category": by_category
    }
