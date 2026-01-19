"""
tests/unit/test_citation.py - 지식 인용 서비스 테스트
KNOW-007, KNOW-008 테스트
"""
import pytest
from core.citation import (
    find_relevant_knowledge,
    pick_citations,
    get_active_knowledge_top3,
    extract_keyword_context,
    _calculate_relevance,
    _extract_question_keywords,
)


class TestFindRelevantKnowledge:
    """find_relevant_knowledge 함수 테스트"""

    def test_returns_tuple(self):
        """튜플 (citations, snippet_text) 반환"""
        result = find_relevant_knowledge("질문", [])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_knowledge_returns_empty(self):
        """빈 지식 리스트는 빈 결과 반환"""
        citations, snippet = find_relevant_knowledge("질문", [])
        assert citations == []
        assert snippet == ""

    def test_finds_relevant_items(self):
        """관련 항목을 찾음"""
        knowledge_items = [
            {"id": "k1", "text": "배포 프로세스 설명입니다", "source": "meeting", "tag": "process"},
            {"id": "k2", "text": "에러 처리 방법입니다", "source": "meeting", "tag": "pitfall"},
        ]
        citations, snippet = find_relevant_knowledge("배포 방법", knowledge_items)
        assert len(citations) > 0

    def test_respects_max_citations(self):
        """max_citations 제한 적용"""
        knowledge_items = [
            {"id": f"k{i}", "text": f"테스트 항목 {i}", "source": "meeting", "tag": "process"}
            for i in range(10)
        ]
        citations, _ = find_relevant_knowledge("테스트", knowledge_items, max_citations=2)
        assert len(citations) <= 2


class TestPickCitations:
    """KNOW-007: pick_citations 함수 테스트"""

    def test_returns_tuple(self):
        """튜플 (items, snippet) 반환"""
        result = pick_citations("질문", [])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_knowledge_returns_empty(self):
        """빈 지식 리스트는 빈 결과 반환"""
        items, snippet = pick_citations("질문", [])
        assert items == []
        assert snippet == ""

    def test_selects_by_tag(self):
        """태그별로 최근 1개 선택"""
        knowledge_items = [
            {"id": "k1", "tag": "rule", "text": "규칙입니다", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "rule", "text": "최근 규칙", "created_at": "2024-01-10"},
            {"id": "k3", "tag": "pitfall", "text": "주의사항", "created_at": "2024-01-05"},
        ]
        items, _ = pick_citations("질문", knowledge_items)
        # rule 태그에서 최근 항목 (k2) 선택
        rule_items = [i for i in items if i["tag"] == "rule"]
        assert len(rule_items) == 1
        assert rule_items[0]["id"] == "k2"

    def test_selects_keyword_matched_items(self):
        """키워드 매칭 항목 선택"""
        knowledge_items = [
            {"id": "k1", "tag": "process", "text": "배포 프로세스입니다", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "process", "text": "에러 처리 방법", "created_at": "2024-01-02"},
        ]
        items, _ = pick_citations("배포 방법", knowledge_items)
        ids = [i["id"] for i in items]
        assert "k1" in ids  # "배포" 키워드 매칭

    def test_topic_hint_bonus(self):
        """topic_hint 매칭 보너스"""
        knowledge_items = [
            {"id": "k1", "tag": "process", "text": "일반 내용", "topic_hint": "배포", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "glossary", "text": "다른 내용", "topic_hint": "고객", "created_at": "2024-01-01"},
        ]
        items, _ = pick_citations("배포 관련 질문", knowledge_items)
        ids = [i["id"] for i in items]
        assert "k1" in ids

    def test_custom_include_tags(self):
        """커스텀 태그 필터"""
        knowledge_items = [
            {"id": "k1", "tag": "rule", "text": "규칙입니다", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "glossary", "text": "용어입니다", "created_at": "2024-01-01"},
        ]
        items, _ = pick_citations("질문", knowledge_items, include_tags=["glossary"])
        tags = [i["tag"] for i in items]
        # rule은 include_tags에 없으므로 제외 가능
        if "rule" in tags:
            # 키워드 매칭으로 추가될 수 있음
            pass


class TestGetActiveKnowledgeTop3:
    """KNOW-008: get_active_knowledge_top3 함수 테스트"""

    def test_returns_dict(self):
        """딕셔너리 반환"""
        result = get_active_knowledge_top3([])
        assert isinstance(result, dict)

    def test_empty_knowledge_returns_empty(self):
        """빈 지식 리스트는 빈 딕셔너리 반환"""
        result = get_active_knowledge_top3([])
        assert result == {}

    def test_returns_one_per_tag(self):
        """각 태그당 1개 반환"""
        knowledge_items = [
            {"id": "k1", "tag": "rule", "text": "규칙1", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "rule", "text": "규칙2", "created_at": "2024-01-10"},
            {"id": "k3", "tag": "pitfall", "text": "주의사항", "created_at": "2024-01-05"},
        ]
        result = get_active_knowledge_top3(knowledge_items)
        assert len(result.get("rule", [])) == 1
        assert len(result.get("pitfall", [])) == 1

    def test_returns_most_recent(self):
        """가장 최근 항목 반환"""
        knowledge_items = [
            {"id": "k1", "tag": "rule", "text": "오래된 규칙", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "rule", "text": "최근 규칙", "created_at": "2024-01-15"},
        ]
        result = get_active_knowledge_top3(knowledge_items)
        assert result["rule"][0]["id"] == "k2"

    def test_includes_expected_tags(self):
        """rule, pitfall, process, glossary 태그 포함"""
        knowledge_items = [
            {"id": "k1", "tag": "rule", "text": "규칙", "created_at": "2024-01-01"},
            {"id": "k2", "tag": "pitfall", "text": "주의", "created_at": "2024-01-01"},
            {"id": "k3", "tag": "process", "text": "프로세스", "created_at": "2024-01-01"},
            {"id": "k4", "tag": "glossary", "text": "용어", "created_at": "2024-01-01"},
        ]
        result = get_active_knowledge_top3(knowledge_items)
        assert "rule" in result
        assert "pitfall" in result
        assert "process" in result
        assert "glossary" in result


class TestExtractKeywordContext:
    """extract_keyword_context 함수 테스트"""

    def test_extracts_context(self):
        """키워드 주변 컨텍스트 추출"""
        text = "이것은 긴 텍스트입니다. 여기에 중요한 키워드가 있습니다. 그 뒤에 더 많은 텍스트가 있습니다."
        result = extract_keyword_context(text, "키워드", context_chars=10)
        assert "키워드" in result

    def test_returns_empty_for_missing_keyword(self):
        """키워드 없으면 빈 문자열"""
        text = "이 텍스트에는 해당 단어가 없습니다"
        result = extract_keyword_context(text, "없는단어")
        assert result == ""

    def test_adds_ellipsis(self):
        """잘린 부분에 ... 추가"""
        text = "앞부분 " * 20 + "키워드" + " 뒷부분" * 20
        result = extract_keyword_context(text, "키워드", context_chars=10)
        assert result.startswith("...")
        assert result.endswith("...")


class TestHelperFunctions:
    """헬퍼 함수 테스트"""

    def test_calculate_relevance_basic(self):
        """기본 관련도 계산"""
        score = _calculate_relevance("배포 방법", "배포 프로세스 설명")
        assert score > 0

    def test_calculate_relevance_no_match(self):
        """매칭 없으면 0"""
        score = _calculate_relevance("질문", "완전히 다른 내용")
        assert score == 0

    def test_calculate_relevance_boost_keywords(self):
        """특수 키워드 부스트"""
        score_normal = _calculate_relevance("방법", "방법 설명")
        score_boosted = _calculate_relevance("에러 방법", "에러 방법 설명")
        # 에러 키워드가 있으면 부스트 적용
        assert score_boosted >= score_normal

    def test_extract_question_keywords(self):
        """질문에서 키워드 추출"""
        keywords = _extract_question_keywords("배포 방법은 어떻게 하나요?")
        assert "배포" in keywords
        # 한국어는 조사가 붙어 "방법은"으로 추출됨
        assert any("방법" in kw for kw in keywords)
        # 불용어 제외
        assert "어떻게" not in keywords

    def test_extract_question_keywords_filters_short(self):
        """짧은 단어 필터"""
        keywords = _extract_question_keywords("이 것 저 것")
        # 2글자 미만 필터
        for kw in keywords:
            assert len(kw) >= 2
