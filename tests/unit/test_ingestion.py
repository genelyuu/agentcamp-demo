"""
tests/unit/test_ingestion.py - 데이터 수집 파이프라인 테스트
KNOW-001 ~ KNOW-006 테스트
"""
import pytest
from ingestion import (
    extract_knowledge,
    apply_tag_limit,
    get_knowledge_stats,
    MIN_TEXT_LENGTH,
    STOP_PHRASES,
    MAX_ITEMS_PER_TAG,
    _is_stop_phrase,
    _classify_tag,
    _extract_signals,
    _extract_topic_hint,
)


class TestExtractKnowledge:
    """KNOW-001 ~ KNOW-004: extract_knowledge 함수 테스트"""

    def test_returns_list(self):
        """extract_knowledge는 리스트를 반환해야 함"""
        result = extract_knowledge("meeting_stt", "테스트 텍스트입니다")
        assert isinstance(result, list)

    def test_uuid4_id_generation(self):
        """KNOW-001: UUID4 ID 생성"""
        result = extract_knowledge("meeting_stt", "테스트 텍스트입니다 길이가 충분해야")
        assert len(result) > 0
        assert "id" in result[0]
        # UUID4는 32자리 hex 문자열
        assert len(result[0]["id"]) == 32

    def test_unique_ids(self):
        """KNOW-001: 각 항목은 고유한 ID를 가져야 함"""
        text = "첫번째 줄 충분한 길이\n두번째 줄 충분한 길이\n세번째 줄 충분한 길이"
        result = extract_knowledge("meeting_stt", text)
        ids = [item["id"] for item in result]
        assert len(ids) == len(set(ids))  # 모두 고유

    def test_min_length_filter(self):
        """KNOW-002: 최소 길이 필터 (10자 미만 제거)"""
        text = "짧은\n이것은 충분히 긴 텍스트입니다"
        result = extract_knowledge("meeting_stt", text)
        for item in result:
            assert len(item["text"]) >= MIN_TEXT_LENGTH

    def test_stop_phrase_filter(self):
        """KNOW-003: Stop phrase 필터"""
        text = "네네\n알겠습니다\n이것은 유효한 지식 텍스트입니다"
        result = extract_knowledge("meeting_stt", text)
        for item in result:
            assert item["text"] not in STOP_PHRASES

    def test_duplicate_skip(self):
        """KNOW-004: 중복 텍스트 스킵"""
        text = "중복된 텍스트입니다 길이 충분\n중복된 텍스트입니다 길이 충분"
        result = extract_knowledge("meeting_stt", text)
        texts = [item["text"] for item in result]
        assert len(texts) == len(set(texts))  # 중복 없음

    def test_existing_texts_skip(self):
        """KNOW-004: 기존 텍스트와 중복 스킵"""
        existing = {"이미 있는 텍스트입니다 충분한 길이"}
        text = "이미 있는 텍스트입니다 충분한 길이\n새로운 텍스트입니다 충분한 길이"
        result = extract_knowledge("meeting_stt", text, existing)
        texts = [item["text"] for item in result]
        assert "이미 있는 텍스트입니다 충분한 길이" not in texts


class TestKnowledgeMetadata:
    """KNOW-006: 메타데이터 필드 테스트"""

    def test_has_created_at(self):
        """created_at 타임스탬프 필드"""
        result = extract_knowledge("meeting_stt", "테스트 텍스트입니다 충분한 길이")
        assert len(result) > 0
        assert "created_at" in result[0]

    def test_has_text_len(self):
        """text_len 필드"""
        result = extract_knowledge("meeting_stt", "테스트 텍스트입니다 충분한 길이")
        assert len(result) > 0
        assert "text_len" in result[0]
        assert result[0]["text_len"] == len(result[0]["text"])

    def test_has_signals(self):
        """signals 필드"""
        result = extract_knowledge("meeting_stt", "테스트 텍스트입니다 충분한 길이")
        assert len(result) > 0
        assert "signals" in result[0]
        assert isinstance(result[0]["signals"], dict)

    def test_has_topic_hint(self):
        """topic_hint 필드"""
        result = extract_knowledge("meeting_stt", "배포 관련 테스트 텍스트입니다")
        assert len(result) > 0
        assert "topic_hint" in result[0]


class TestApplyTagLimit:
    """KNOW-005: Tag별 Top-K 유지 테스트"""

    def test_limits_items_per_tag(self):
        """각 tag당 최대 개수 제한"""
        items = [
            {"id": f"item_{i}", "tag": "pitfall", "created_at": f"2024-01-{i:02d}"}
            for i in range(1, 40)
        ]
        result = apply_tag_limit(items, max_per_tag=30)
        pitfall_count = sum(1 for item in result if item["tag"] == "pitfall")
        assert pitfall_count == 30

    def test_keeps_recent_items(self):
        """최근 항목을 유지"""
        items = [
            {"id": f"item_{i}", "tag": "rule", "created_at": f"2024-01-{i:02d}"}
            for i in range(1, 10)
        ]
        result = apply_tag_limit(items, max_per_tag=3)
        # 최근 3개만 유지 (created_at 기준)
        assert len(result) == 3
        ids = [item["id"] for item in result]
        assert "item_7" in ids
        assert "item_8" in ids
        assert "item_9" in ids


class TestHelperFunctions:
    """헬퍼 함수 테스트"""

    def test_is_stop_phrase_exact_match(self):
        """정확한 stop phrase 매칭"""
        assert _is_stop_phrase("네네") is True
        assert _is_stop_phrase("알겠습니다") is True

    def test_is_stop_phrase_with_whitespace(self):
        """공백 포함 stop phrase"""
        assert _is_stop_phrase("  네네  ") is True

    def test_is_stop_phrase_special_chars(self):
        """특수문자만 있는 경우"""
        assert _is_stop_phrase("ㅋㅋㅋㅋ") is True
        assert _is_stop_phrase("...") is True

    def test_classify_tag_pitfall(self):
        """pitfall 태그 분류"""
        assert _classify_tag("이 error가 발생했습니다") == "pitfall"
        assert _classify_tag("버그가 있습니다") == "pitfall"

    def test_classify_tag_rule(self):
        """rule 태그 분류"""
        assert _classify_tag("이것은 반드시 해야 합니다") == "rule"
        assert _classify_tag("금지 항목입니다") == "rule"

    def test_classify_tag_glossary(self):
        """glossary 태그 분류"""
        assert _classify_tag("OJT의 정의는 다음과 같습니다") == "glossary"

    def test_classify_tag_default_process(self):
        """기본값은 process"""
        assert _classify_tag("일반적인 텍스트입니다") == "process"

    def test_extract_signals_has_number(self):
        """숫자 포함 시그널"""
        signals = _extract_signals("버전 1.2.3 입니다")
        assert signals["has_number"] is True

    def test_extract_signals_has_error_code(self):
        """에러 코드 시그널"""
        signals = _extract_signals("error 500 발생")
        assert signals["has_error_code"] is True

    def test_extract_signals_has_must_word(self):
        """필수 키워드 시그널"""
        signals = _extract_signals("반드시 확인해야 합니다")
        assert signals["has_must_word"] is True

    def test_extract_signals_has_url(self):
        """URL 시그널"""
        signals = _extract_signals("자세한 내용은 https://example.com 참고")
        assert signals["has_url"] is True

    def test_extract_topic_hint_deploy(self):
        """배포 토픽 힌트"""
        assert _extract_topic_hint("배포 파이프라인 설정") == "배포"

    def test_extract_topic_hint_customer(self):
        """고객 토픽 힌트"""
        assert _extract_topic_hint("고객 요청 사항입니다") == "고객"

    def test_extract_topic_hint_none(self):
        """토픽 힌트 없음"""
        assert _extract_topic_hint("일반 텍스트") is None


class TestGetKnowledgeStats:
    """get_knowledge_stats 함수 테스트"""

    def test_returns_total_count(self):
        """총 개수 반환"""
        items = [
            {"tag": "rule", "source": "meeting_stt"},
            {"tag": "pitfall", "source": "slack_discord"},
        ]
        stats = get_knowledge_stats(items)
        assert stats["total"] == 2

    def test_returns_by_tag_counts(self):
        """태그별 카운트"""
        items = [
            {"tag": "rule", "source": "meeting_stt"},
            {"tag": "rule", "source": "meeting_stt"},
            {"tag": "pitfall", "source": "slack_discord"},
        ]
        stats = get_knowledge_stats(items)
        assert stats["by_tag"]["rule"] == 2
        assert stats["by_tag"]["pitfall"] == 1

    def test_returns_by_source_counts(self):
        """소스별 카운트"""
        items = [
            {"tag": "rule", "source": "meeting_stt"},
            {"tag": "pitfall", "source": "slack_discord"},
        ]
        stats = get_knowledge_stats(items)
        assert stats["by_source"]["meeting_stt"] == 1
        assert stats["by_source"]["slack_discord"] == 1
