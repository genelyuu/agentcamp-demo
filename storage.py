"""
storage.py - JSON 저장소 모듈 (Backward Compatibility Wrapper)
ARCH-007: 기존 모듈 래퍼 유지
참조: core/storage.py
"""
from core.storage import (
    DATA_DIR,
    ORG_PATH,
    KNOW_PATH,
    SESS_PATH,
    load_json,
    save_json,
    get_org,
    set_org,
    get_knowledge,
    set_knowledge,
    get_sessions,
    set_sessions,
)

__all__ = [
    "DATA_DIR",
    "ORG_PATH",
    "KNOW_PATH",
    "SESS_PATH",
    "load_json",
    "save_json",
    "get_org",
    "set_org",
    "get_knowledge",
    "set_knowledge",
    "get_sessions",
    "set_sessions",
]
