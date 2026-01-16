"""
ingestion.py - 데이터 수집 파이프라인 모듈
책임: STT/슬랙 텍스트에서 지식 항목 추출
"""
import time
from typing import Any, Dict, List


def extract_knowledge(source_type: str, text: str) -> List[Dict[str, Any]]:
    """
    텍스트에서 지식 항목 추출

    Args:
        source_type: 소스 타입 (meeting_stt, slack_discord, client_stt)
        text: 원본 텍스트

    Returns:
        지식 항목 리스트 [{id, source, tag, text}, ...]
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines[:50]):  # 최대 50개 처리
        tag = _classify_tag(line)
        items.append({
            "id": f"{source_type}-{int(time.time() * 1000)}-{idx}",
            "source": source_type,
            "tag": tag,
            "text": line,
        })

    return items


def _classify_tag(text: str) -> str:
    """텍스트 태그 분류"""
    lower_text = text.lower()

    # pitfall 감지
    if any(kw in lower_text for kw in ["error", "fail"]) or \
       any(kw in text for kw in ["버그", "실수"]):
        return "pitfall"

    # glossary 감지
    if any(kw in text for kw in ["정의", "용어"]):
        return "glossary"

    # rule 감지
    if any(kw in text for kw in ["해야", "금지", "원칙"]):
        return "rule"

    # 기본값
    return "process"
