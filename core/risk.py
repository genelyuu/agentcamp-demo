"""
core/risk.py - 리스크 레지스터 CRUD API
RISK-006: Risk Register CRUD API
ADR-105: Risk Register
DUP-002: BaseJSONRepository 활용
"""
import os
from typing import List, Optional
from datetime import datetime

from schemas import RiskEntry, RiskRegister, RiskCategory
from .repository import BaseJSONRepository

# 파일 경로
RISK_PATH = os.path.join("data", "risk_register.json")

# Repository 인스턴스 (내부 구현)
_repo = BaseJSONRepository[RiskEntry](
    path=RISK_PATH,
    container_cls=RiskRegister,
    item_key="risks"
)


# ============================================================
# Legacy Functions (Facade) - 외부 API 호환성 유지
# ============================================================

def _ensure_file() -> None:
    """파일 존재 확인 및 생성 (Legacy 호환)"""
    _repo._ensure_file()


def _load_register() -> RiskRegister:
    """리스크 레지스터 로드 (Legacy 호환)"""
    return _repo._load()


def _save_register(register: RiskRegister) -> None:
    """리스크 레지스터 저장 (Legacy 호환)"""
    _repo._save(register)


# ============================================================
# CRUD Operations
# ============================================================

def get_all_risks() -> List[RiskEntry]:
    """모든 리스크 조회"""
    return _repo.get_all()


def get_risk(risk_id: str) -> Optional[RiskEntry]:
    """특정 리스크 조회"""
    return _repo.get_by_id(risk_id, id_field="risk_id")


def create_risk(risk: RiskEntry) -> RiskEntry:
    """리스크 생성"""
    return _repo.create(risk)


def update_risk(risk_id: str, updates: dict) -> Optional[RiskEntry]:
    """리스크 수정"""
    # updated_at 자동 갱신
    updates["updated_at"] = datetime.utcnow().isoformat()
    return _repo.update(
        item_id=risk_id,
        updates=updates,
        id_field="risk_id",
        item_cls=RiskEntry
    )


def delete_risk(risk_id: str) -> bool:
    """리스크 삭제"""
    return _repo.delete(risk_id, id_field="risk_id")


# ============================================================
# Query Operations
# ============================================================

def get_risks_by_category(category: RiskCategory) -> List[RiskEntry]:
    """카테고리별 리스크 조회"""
    return _repo.filter(lambda r: r.category == category)


def get_risks_by_status(status: str) -> List[RiskEntry]:
    """상태별 리스크 조회"""
    return _repo.filter(lambda r: r.status == status)


def get_high_risks(threshold: int = 12) -> List[RiskEntry]:
    """높은 리스크 조회 (score >= threshold)"""
    return _repo.filter(lambda r: r.risk_score >= threshold)


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
