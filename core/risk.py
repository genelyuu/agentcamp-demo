"""
core/risk.py - 리스크 레지스터 CRUD API
RISK-006: Risk Register CRUD API
ADR-105: Risk Register
"""
import json
import os
from typing import List, Optional
from datetime import datetime

from schemas import RiskEntry, RiskRegister, RiskCategory

# 파일 경로
RISK_PATH = os.path.join("data", "risk_register.json")


def _ensure_file() -> None:
    """파일 존재 확인 및 생성"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(RISK_PATH):
        with open(RISK_PATH, "w", encoding="utf-8") as f:
            json.dump({"risks": []}, f, ensure_ascii=False, indent=2)


def _load_register() -> RiskRegister:
    """리스크 레지스터 로드"""
    _ensure_file()
    with open(RISK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RiskRegister(**data)


def _save_register(register: RiskRegister) -> None:
    """리스크 레지스터 저장"""
    _ensure_file()
    with open(RISK_PATH, "w", encoding="utf-8") as f:
        json.dump(register.model_dump(mode="json"), f, ensure_ascii=False, indent=2)


# CRUD Operations

def get_all_risks() -> List[RiskEntry]:
    """모든 리스크 조회"""
    register = _load_register()
    return register.risks


def get_risk(risk_id: str) -> Optional[RiskEntry]:
    """특정 리스크 조회"""
    risks = get_all_risks()
    for risk in risks:
        if risk.risk_id == risk_id:
            return risk
    return None


def create_risk(risk: RiskEntry) -> RiskEntry:
    """리스크 생성"""
    register = _load_register()
    register.risks.append(risk)
    _save_register(register)
    return risk


def update_risk(risk_id: str, updates: dict) -> Optional[RiskEntry]:
    """리스크 수정"""
    register = _load_register()

    for i, risk in enumerate(register.risks):
        if risk.risk_id == risk_id:
            # 기존 데이터에 업데이트 적용
            risk_dict = risk.model_dump()
            risk_dict.update(updates)
            risk_dict["updated_at"] = datetime.utcnow().isoformat()

            # 새 객체 생성
            updated_risk = RiskEntry(**risk_dict)
            register.risks[i] = updated_risk
            _save_register(register)
            return updated_risk

    return None


def delete_risk(risk_id: str) -> bool:
    """리스크 삭제"""
    register = _load_register()
    original_count = len(register.risks)

    register.risks = [r for r in register.risks if r.risk_id != risk_id]

    if len(register.risks) < original_count:
        _save_register(register)
        return True
    return False


# Query Operations

def get_risks_by_category(category: RiskCategory) -> List[RiskEntry]:
    """카테고리별 리스크 조회"""
    risks = get_all_risks()
    return [r for r in risks if r.category == category]


def get_risks_by_status(status: str) -> List[RiskEntry]:
    """상태별 리스크 조회"""
    risks = get_all_risks()
    return [r for r in risks if r.status == status]


def get_high_risks(threshold: int = 12) -> List[RiskEntry]:
    """높은 리스크 조회 (score >= threshold)"""
    risks = get_all_risks()
    return [r for r in risks if r.risk_score >= threshold]


def get_risk_summary() -> dict:
    """리스크 요약 통계"""
    risks = get_all_risks()

    if not risks:
        return {
            "total": 0,
            "by_status": {},
            "by_level": {},
            "avg_score": 0,
            "high_risk_count": 0
        }

    by_status = {}
    by_level = {}

    for risk in risks:
        # 상태별 집계
        status = risk.status
        by_status[status] = by_status.get(status, 0) + 1

        # 레벨별 집계
        level = risk.risk_level
        by_level[level] = by_level.get(level, 0) + 1

    avg_score = sum(r.risk_score for r in risks) / len(risks)
    high_risk_count = len([r for r in risks if r.risk_score >= 12])

    return {
        "total": len(risks),
        "by_status": by_status,
        "by_level": by_level,
        "avg_score": round(avg_score, 1),
        "high_risk_count": high_risk_count
    }
