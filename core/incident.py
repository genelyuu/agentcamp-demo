"""
core/incident.py - 인시던트 로그 CRUD API
RISK-007: Incident Log CRUD API
ADR-105: Risk Register
"""
import json
import os
from typing import List, Optional
from datetime import datetime

from schemas import Incident, IncidentLog, IncidentStatus, RiskCategory, Severity

# 파일 경로
INCIDENT_PATH = os.path.join("data", "incidents.json")


def _ensure_file() -> None:
    """파일 존재 확인 및 생성"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(INCIDENT_PATH):
        with open(INCIDENT_PATH, "w", encoding="utf-8") as f:
            json.dump({"incidents": []}, f, ensure_ascii=False, indent=2)


def _load_log() -> IncidentLog:
    """인시던트 로그 로드"""
    _ensure_file()
    with open(INCIDENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return IncidentLog(**data)


def _save_log(log: IncidentLog) -> None:
    """인시던트 로그 저장"""
    _ensure_file()
    with open(INCIDENT_PATH, "w", encoding="utf-8") as f:
        json.dump(log.model_dump(mode="json"), f, ensure_ascii=False, indent=2)


# CRUD Operations

def get_all_incidents() -> List[Incident]:
    """모든 인시던트 조회"""
    log = _load_log()
    return log.incidents


def get_incident(incident_id: str) -> Optional[Incident]:
    """특정 인시던트 조회"""
    incidents = get_all_incidents()
    for incident in incidents:
        if incident.incident_id == incident_id:
            return incident
    return None


def create_incident(incident: Incident) -> Incident:
    """인시던트 생성"""
    log = _load_log()
    log.incidents.append(incident)
    _save_log(log)
    return incident


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
    log = _load_log()

    for i, incident in enumerate(log.incidents):
        if incident.incident_id == incident_id:
            incident_dict = incident.model_dump()
            incident_dict["status"] = status

            if mitigation:
                incident_dict["mitigation"] = mitigation
            if rca:
                incident_dict["rca"] = rca

            if status == IncidentStatus.RESOLVED:
                incident_dict["resolved_at"] = datetime.utcnow().isoformat()

            updated_incident = Incident(**incident_dict)
            log.incidents[i] = updated_incident
            _save_log(log)
            return updated_incident

    return None


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


# Query Operations

def get_open_incidents() -> List[Incident]:
    """열린 인시던트 조회"""
    incidents = get_all_incidents()
    return [i for i in incidents if i.status == IncidentStatus.OPEN]


def get_incidents_by_category(category: RiskCategory) -> List[Incident]:
    """카테고리별 인시던트 조회"""
    incidents = get_all_incidents()
    return [i for i in incidents if i.category == category]


def get_incidents_by_severity(severity: Severity) -> List[Incident]:
    """심각도별 인시던트 조회"""
    incidents = get_all_incidents()
    return [i for i in incidents if i.severity == severity]


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

    open_count = len([i for i in incidents if i.status == IncidentStatus.OPEN])
    resolved_count = len([i for i in incidents if i.status == IncidentStatus.RESOLVED])

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
