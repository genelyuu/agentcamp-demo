"""
core/storage.py - JSON 저장소 모듈
ARCH-005: storage.py → core/storage.py 마이그레이션
ADR-101: UI/Core Boundary Separation
LOG-003: 로깅 적용
"""
import json
import os
from typing import Any, Dict

from schemas import OrgConfig, KnowledgeBase, SessionStore
from .logger import get_logger

logger = get_logger("storage")

DATA_DIR = "data"
ORG_PATH = os.path.join(DATA_DIR, "org.json")
KNOW_PATH = os.path.join(DATA_DIR, "knowledge.json")
SESS_PATH = os.path.join(DATA_DIR, "sessions.json")

# 기본값 정의
_DEFAULTS = {
    ORG_PATH: {
        "company": "Veluga",
        "role": "Backend Engineer",
        "tools": ["Slack", "GitHub"],
        "rubric": {"acceptance_keywords": ["원인", "재현", "재발방지", "로그"]}
    },
    KNOW_PATH: {"items": []},
    SESS_PATH: {"users": {}}
}


def _ensure() -> None:
    """데이터 디렉토리 및 기본 파일 생성"""
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, default in _DEFAULTS.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)


def load_json(path: str) -> Dict[str, Any]:
    """JSON 파일 로드"""
    _ensure()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Loaded JSON: path={path}")
            return data
    except Exception as e:
        logger.error(f"Failed to load JSON: path={path}, error={str(e)}")
        raise


def save_json(path: str, obj: Dict[str, Any]) -> None:
    """JSON 파일 저장"""
    _ensure()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        logger.debug(f"Saved JSON: path={path}")
    except Exception as e:
        logger.error(f"Failed to save JSON: path={path}, error={str(e)}")
        raise


def get_org() -> Dict[str, Any]:
    """조직 설정 조회"""
    return load_json(ORG_PATH)


def set_org(new_org: Dict[str, Any]) -> None:
    """조직 설정 저장"""
    save_json(ORG_PATH, new_org)


def get_knowledge() -> Dict[str, Any]:
    """지식 베이스 조회"""
    return load_json(KNOW_PATH)


def set_knowledge(new_know: Dict[str, Any]) -> None:
    """지식 베이스 저장"""
    save_json(KNOW_PATH, new_know)


def get_sessions() -> Dict[str, Any]:
    """세션 정보 조회"""
    return load_json(SESS_PATH)


def set_sessions(new_sess: Dict[str, Any]) -> None:
    """세션 정보 저장"""
    save_json(SESS_PATH, new_sess)


# Pydantic 모델 기반 헬퍼 함수
def get_org_config() -> OrgConfig:
    """OrgConfig Pydantic 모델로 조회"""
    data = get_org()
    return OrgConfig(**data)


def set_org_config(config: OrgConfig) -> None:
    """OrgConfig Pydantic 모델로 저장"""
    set_org(config.model_dump())


def get_knowledge_base() -> KnowledgeBase:
    """KnowledgeBase Pydantic 모델로 조회"""
    data = get_knowledge()
    return KnowledgeBase(**data)


def set_knowledge_base(kb: KnowledgeBase) -> None:
    """KnowledgeBase Pydantic 모델로 저장"""
    set_knowledge(kb.model_dump())


def get_session_store() -> SessionStore:
    """SessionStore Pydantic 모델로 조회"""
    data = get_sessions()
    return SessionStore(**data)


def set_session_store(store: SessionStore) -> None:
    """SessionStore Pydantic 모델로 저장"""
    set_sessions(store.model_dump())
