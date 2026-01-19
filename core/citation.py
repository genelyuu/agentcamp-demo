"""
core/citation.py - 지식 인용 서비스
ADR-106: Citation Transparency - 지식 인용 투명성
책임: 질문/제출에 관련된 지식 항목을 찾고 인용 정보 생성

SOLID 원칙:
- SRP: 인용 로직만 담당
- OCP: 새로운 매칭 알고리즘 추가 시 확장 가능
- DIP: 스키마에 의존
"""
from typing import Any, Dict, List, Tuple

from schemas import Citation, KnowledgeItem

from .logger import get_logger

logger = get_logger("citation")


def find_relevant_knowledge(
    question: str,
    knowledge_items: List[Dict[str, Any]],
    max_citations: int = 3
) -> Tuple[List[Citation], str]:
    """
    질문과 관련된 지식 항목을 찾아 인용 정보 생성

    Args:
        question: 사용자 질문
        knowledge_items: 지식 항목 리스트 (Dict 형태)
        max_citations: 최대 인용 수

    Returns:
        (인용 리스트, 지식 스니펫 문자열)
    """
    if not knowledge_items:
        logger.debug("No knowledge items available for citation")
        return [], ""

    question_lower = question.lower()
    scored_items: List[Tuple[float, Dict[str, Any]]] = []

    for item in knowledge_items:
        text = item.get("text", "")
        score = _calculate_relevance(question_lower, text.lower())
        if score > 0:
            scored_items.append((score, item))

    # 점수순 정렬
    scored_items.sort(key=lambda x: x[0], reverse=True)

    citations: List[Citation] = []
    snippets: List[str] = []

    for score, item in scored_items[:max_citations]:
        citation = Citation(
            knowledge_id=item.get("id", f"k_{len(citations)}"),
            text=item.get("text", "")[:200],  # 최대 200자
            source=item.get("source", "unknown"),
            tag=item.get("tag", "unknown"),
            relevance_score=min(1.0, score)
        )
        citations.append(citation)
        snippets.append(item.get("text", ""))

    # 스니펫 없으면 최근 항목 사용 (fallback)
    if not snippets and knowledge_items:
        latest = knowledge_items[-1]
        snippets.append(latest.get("text", ""))
        citations.append(Citation(
            knowledge_id=latest.get("id", "k_fallback"),
            text=latest.get("text", "")[:200],
            source=latest.get("source", "unknown"),
            tag=latest.get("tag", "unknown"),
            relevance_score=0.1  # 낮은 관련도
        ))
        logger.debug("Using fallback knowledge item (latest)")

    snippet_text = "\n".join(snippets)
    logger.info(f"Found {len(citations)} relevant knowledge items for question")

    return citations, snippet_text


def _calculate_relevance(question: str, text: str) -> float:
    """
    질문과 텍스트 간의 관련도 점수 계산

    간단한 키워드 매칭 기반 (향후 임베딩/의미 검색으로 확장 가능)
    """
    # 질문에서 주요 키워드 추출 (불용어 제외)
    stopwords = {"이", "가", "을", "를", "은", "는", "에", "의", "로", "와", "과",
                 "하다", "있다", "되다", "어떻게", "무엇", "어떤", "왜", "어디"}

    question_words = set(question.split()) - stopwords
    text_words = set(text.split())

    if not question_words:
        return 0.0

    # 공통 단어 수 / 질문 단어 수
    common = question_words & text_words
    score = len(common) / len(question_words)

    # 특수 키워드 부스트
    boost_keywords = ["장애", "에러", "오류", "버그", "원인", "해결", "방법", "로그"]
    for kw in boost_keywords:
        if kw in question and kw in text:
            score += 0.2

    return min(1.0, score)


def extract_keyword_context(text: str, keyword: str, context_chars: int = 50) -> str:
    """
    텍스트에서 키워드 주변 컨텍스트 추출

    Args:
        text: 전체 텍스트
        keyword: 찾을 키워드
        context_chars: 앞뒤로 포함할 문자 수

    Returns:
        키워드 주변 컨텍스트 문자열
    """
    lower_text = text.lower()
    lower_keyword = keyword.lower()

    pos = lower_text.find(lower_keyword)
    if pos == -1:
        return ""

    start = max(0, pos - context_chars)
    end = min(len(text), pos + len(keyword) + context_chars)

    context = text[start:end]

    # 시작/끝이 잘린 경우 표시
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."

    return context
