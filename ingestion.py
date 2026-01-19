"""
ingestion.py - 데이터 수집 파이프라인 모듈
책임: STT/슬랙 텍스트에서 지식 항목 추출
KNOW-001: uuid4 ID 생성
KNOW-002: 최소 길이 필터
KNOW-003: Stop phrase 필터
KNOW-004: 중복 텍스트 스킵
KNOW-005: Tag별 Top-K 유지
KNOW-006: 메타데이터 필드 추가
"""
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


# ============================================================
# Constants
# ============================================================

# KNOW-002: 최소 길이 (10자 미만 제거)
MIN_TEXT_LENGTH = 10

# KNOW-003: Stop phrases (무의미한 문장)
STOP_PHRASES: Set[str] = {
    # 한국어 추임새/동의
    "맞아요", "맞아", "네네", "네", "응", "응응", "ㅇㅇ", "ㅇㅋ", "ㄱㄱ",
    "알겠습니다", "알겠어요", "알겠어", "그렇죠", "그쵸", "그래요", "그래",
    "좋아요", "좋아", "오케이", "확인", "감사합니다", "감사해요", "고마워요",
    # 영어
    "ok", "okay", "yes", "yeah", "yep", "sure", "got it", "thanks",
    # 이모지/기호만
    "ㅋㅋ", "ㅋㅋㅋ", "ㅎㅎ", "ㅎㅎㅎ", "ㅠㅠ", "ㅜㅜ", "...", "???", "!!!",
}

# KNOW-005: Tag별 최대 개수
MAX_ITEMS_PER_TAG = 30

# KNOW-006: Topic 힌트 키워드
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "배포": ["배포", "deploy", "release", "ci", "cd", "파이프라인"],
    "고객": ["고객", "client", "customer", "유저", "사용자", "user"],
    "UX": ["ux", "ui", "화면", "디자인", "플로우", "flow"],
    "로그": ["로그", "log", "에러", "error", "exception", "오류"],
    "DB": ["db", "database", "쿼리", "query", "테이블", "table"],
    "API": ["api", "엔드포인트", "endpoint", "요청", "request", "응답"],
    "보안": ["보안", "security", "인증", "auth", "권한", "permission"],
    "성능": ["성능", "performance", "최적화", "optimize", "속도", "느림"],
}


# ============================================================
# Main Functions
# ============================================================

def extract_knowledge(
    source_type: str,
    text: str,
    existing_texts: Optional[Set[str]] = None
) -> List[Dict[str, Any]]:
    """
    텍스트에서 지식 항목 추출

    Args:
        source_type: 소스 타입 (meeting_stt, slack_discord, client_stt)
        text: 원본 텍스트
        existing_texts: 기존 지식 텍스트 집합 (중복 체크용)

    Returns:
        지식 항목 리스트
    """
    if existing_texts is None:
        existing_texts = set()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items: List[Dict[str, Any]] = []

    for line in lines[:50]:  # 최대 50개 처리
        # KNOW-002: 최소 길이 필터
        if len(line) < MIN_TEXT_LENGTH:
            continue

        # KNOW-003: Stop phrase 필터
        if _is_stop_phrase(line):
            continue

        # KNOW-004: 중복 텍스트 스킵
        if line in existing_texts:
            continue

        # 태그 분류
        tag = _classify_tag(line)

        # KNOW-006: 메타데이터 생성
        signals = _extract_signals(line)
        topic_hint = _extract_topic_hint(line)

        # KNOW-001: uuid4 ID 생성
        items.append({
            "id": uuid.uuid4().hex,
            "source": source_type,
            "tag": tag,
            "text": line,
            # KNOW-006: 메타데이터 필드
            "created_at": datetime.utcnow().isoformat(),
            "text_len": len(line),
            "signals": signals,
            "topic_hint": topic_hint,
        })

        # 중복 방지를 위해 추가
        existing_texts.add(line)

    return items


def apply_tag_limit(
    items: List[Dict[str, Any]],
    max_per_tag: int = MAX_ITEMS_PER_TAG
) -> List[Dict[str, Any]]:
    """
    KNOW-005: Tag별 Top-K 유지

    각 tag별로 최근 max_per_tag개만 유지합니다.

    Args:
        items: 전체 지식 항목 리스트
        max_per_tag: tag당 최대 개수

    Returns:
        필터링된 지식 항목 리스트
    """
    # Tag별로 그룹화
    tag_groups: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        tag = item.get("tag", "process")
        if tag not in tag_groups:
            tag_groups[tag] = []
        tag_groups[tag].append(item)

    # 각 tag별로 최근 max_per_tag개만 유지
    result: List[Dict[str, Any]] = []
    for tag, group in tag_groups.items():
        # created_at 기준 정렬 (최신이 뒤로)
        sorted_group = sorted(
            group,
            key=lambda x: x.get("created_at", ""),
            reverse=False
        )
        # 최근 max_per_tag개만 유지
        result.extend(sorted_group[-max_per_tag:])

    return result


def get_knowledge_stats(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    지식 베이스 통계 반환

    Args:
        items: 지식 항목 리스트

    Returns:
        통계 딕셔너리
    """
    tag_counts: Dict[str, int] = {}
    source_counts: Dict[str, int] = {}
    topic_counts: Dict[str, int] = {}

    for item in items:
        # Tag 카운트
        tag = item.get("tag", "process")
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Source 카운트
        source = item.get("source", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

        # Topic 카운트
        topic = item.get("topic_hint")
        if topic:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return {
        "total": len(items),
        "by_tag": tag_counts,
        "by_source": source_counts,
        "by_topic": topic_counts,
    }


# ============================================================
# Helper Functions
# ============================================================

def _is_stop_phrase(text: str) -> bool:
    """
    KNOW-003: Stop phrase 여부 확인
    """
    normalized = text.strip().lower()

    # 정확히 일치하는 경우
    if normalized in STOP_PHRASES:
        return True

    # 소문자 변환 후 비교
    if text.strip() in STOP_PHRASES:
        return True

    # 특수문자/이모지만 있는 경우
    if re.match(r'^[ㄱ-ㅎㅏ-ㅣ\W]+$', text):
        return True

    return False


def _classify_tag(text: str) -> str:
    """
    텍스트 태그 분류

    Returns:
        tag: rule, pitfall, glossary, process 중 하나
    """
    lower_text = text.lower()

    # pitfall 감지 (실수/에러 관련)
    pitfall_keywords = ["error", "fail", "exception", "버그", "실수", "오류", "장애", "문제"]
    if any(kw in lower_text for kw in pitfall_keywords):
        return "pitfall"

    # glossary 감지 (용어 정의)
    glossary_keywords = ["정의", "용어", "뜻", "의미", "란", "이란"]
    if any(kw in text for kw in glossary_keywords):
        return "glossary"

    # rule 감지 (규칙/원칙)
    rule_keywords = ["해야", "금지", "원칙", "반드시", "필수", "규칙", "안됨", "하면 안"]
    if any(kw in text for kw in rule_keywords):
        return "rule"

    # 기본값
    return "process"


def _extract_signals(text: str) -> Dict[str, bool]:
    """
    KNOW-006: 텍스트에서 시그널 추출

    Returns:
        signals: {has_number, has_error_code, has_must_word, has_url}
    """
    return {
        "has_number": bool(re.search(r'\d+', text)),
        "has_error_code": bool(re.search(r'(error|err|exception|500|404|403|401)\s*:?\s*\d*', text.lower())),
        "has_must_word": any(kw in text for kw in ["해야", "반드시", "필수", "금지"]),
        "has_url": bool(re.search(r'https?://|www\.', text.lower())),
    }


def _extract_topic_hint(text: str) -> Optional[str]:
    """
    KNOW-006: 텍스트에서 토픽 힌트 추출

    Returns:
        topic_hint: 배포, 고객, UX, 로그, DB, API, 보안, 성능 중 하나 또는 None
    """
    lower_text = text.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower_text for kw in keywords):
            return topic

    return None
