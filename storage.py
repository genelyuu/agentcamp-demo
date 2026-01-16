"""
storage.py - JSON 저장소 모듈
책임: 데모용 JSON 기반 데이터 영속화
"""
import json
import os
from typing import Any, Dict

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
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: Dict[str, Any]) -> None:
    """JSON 파일 저장"""
    _ensure()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


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
