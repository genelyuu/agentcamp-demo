"""
core/orchestrator.py - 질문 라우팅 & 답변 생성 모듈
ARCH-003: orchestrator.py → core/ 마이그레이션
ADR-101: UI/Core Boundary Separation
ADR-106: Citation Transparency - 지식 인용 투명성
ADR-108: Explainable Routing - 설명가능 라우팅
ADR-110: Offline-first + LLM-enhanced 아키텍처
LOG-003: 로깅 적용
ERR-TYPE-001: 타입 힌트 강화 (Dict → Union[Dict, OrgConfig])

SOLID 원칙:
- SRP: 라우팅/답변생성/LLM확장 각각 분리
- OCP: 새 LLM provider 추가 시 확장 가능
- DIP: BaseLLMClient 추상화에 의존
"""
import math
import time
from typing import Any, Dict, List, Optional, Union

from agents import TwinAgent
from llm_client import BaseLLMClient, MockLLMClient, create_llm_client
from schemas import OrgConfig, AnswerResult, Citation
from schemas.routing import Candidate, RoutingResult

from .logger import get_logger
from .citation import find_relevant_knowledge, pick_citations
from .twin_renderer import render_twin_answer, StructuredAnswer

logger = get_logger("orchestrator")

# 라우팅 키워드 정의 (기존 호환용)
_ROUTING_RULES: Dict[str, list[str]] = {
    "Sam Lee": ["우선순위", "전략", "고객", "리스크", "비용"],
    "JH Kim": ["요구사항", "스코프", "정의", "kpi", "지표"],
    "Seul Kim": ["ui", "ux", "화면", "프론트", "component", "반응형"],
}

# 확장된 라우팅 사전 (ADR-108: Explainable Routing)
ROUTING_LEXICON: Dict[str, List[str]] = {
    # CEO/대표 - 전략/의사결정/승인 관련
    "Sam Lee": [
        "우선순위", "전략", "고객", "리스크", "비용",
        "결정", "승인", "사업", "임팩트", "방향", "투자"
    ],
    # PM - 요구사항/스코프/지표 관련
    "JH Kim": [
        "요구사항", "스코프", "정의", "kpi", "지표",
        "ac", "acceptance", "성공조건", "가설", "실험", "mvp"
    ],
    # Frontend - UI/UX/화면 관련
    "Seul Kim": [
        "ui", "ux", "화면", "프론트", "component", "반응형",
        "에러케이스", "동선", "copy", "메시지", "디자인", "인터랙션"
    ],
    # Backend - 시스템/성능/안정성 관련
    "Jin Park": [
        "로그", "log", "에러", "error", "500", "db",
        "timeout", "latency", "성능", "메트릭", "trace",
        "롤백", "배포", "서버", "api"
    ],
}

# 글로벌 LLM 클라이언트 (기본: Mock)
_llm_client: BaseLLMClient = MockLLMClient()


def set_llm_client(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> None:
    """
    LLM 클라이언트 설정

    Args:
        provider: "mock", "claude", "openai"
        api_key: API 키
        model: 모델명 (선택)
    """
    global _llm_client
    logger.info(f"Setting LLM client: provider={provider}, model={model or 'default'}")
    _llm_client = create_llm_client(provider, api_key, model)
    logger.info(f"LLM client set successfully: {type(_llm_client).__name__}")


def get_llm_client() -> BaseLLMClient:
    """현재 LLM 클라이언트 반환"""
    return _llm_client


def route_agent(question: str) -> str:
    """
    질문 내용 기반 Digital Twin 라우팅 (기존 호환용)

    Args:
        question: 사용자 질문

    Returns:
        선택된 Twin 이름
    """
    q_lower = question.lower()

    for twin_name, keywords in _ROUTING_RULES.items():
        if any(kw in q_lower for kw in keywords):
            logger.debug(f"Routed to {twin_name}: question='{question[:50]}...'")
            return twin_name

    # 기본값: Backend (Jin Park)
    logger.debug(f"Default routing to Jin Park: question='{question[:50]}...'")
    return "Jin Park"


def _match_keywords(question: str, keywords: List[str]) -> List[str]:
    """질문에서 키워드 매칭 (ADR-108)"""
    q_lower = question.lower()
    return [kw for kw in keywords if kw.lower() in q_lower]


def _calculate_routing_score(hits: List[str], total: int) -> float:
    """
    라우팅 점수 계산 (ADR-108)

    sqrt를 사용하여 완만하게 증가 (과대확신 방지)
    """
    if total <= 0:
        return 0.0
    return min(1.0, math.sqrt(len(hits) / total))


def route_agent_with_reason(
    question: str,
    twins: Dict[str, TwinAgent],
    top_k: int = 2,
) -> RoutingResult:
    """
    설명가능 라우팅 - 근거/점수/대안 후보 포함 (ADR-108)

    Args:
        question: 사용자 질문
        twins: Twin 딕셔너리 (name -> TwinAgent)
        top_k: 상위 후보 수

    Returns:
        RoutingResult (선택 트윈 + 점수 + 근거 + 대안)
    """
    candidates: List[Candidate] = []

    for name in twins.keys():
        lexicon = ROUTING_LEXICON.get(name, [])
        hits = _match_keywords(question, lexicon)
        score = _calculate_routing_score(hits, total=len(lexicon))
        candidates.append(Candidate(
            name=name,
            score=score,
            matched_keywords=hits
        ))

    # 점수 내림차순 정렬 (tie-breaker: 매칭 키워드 수)
    candidates.sort(
        key=lambda c: (c.score, len(c.matched_keywords)),
        reverse=True
    )

    best = candidates[0]
    top = candidates[:max(1, top_k)]

    # 사람이 읽을 수 있는 근거 생성
    reason_parts = []
    if best.matched_keywords:
        kw_str = ", ".join(best.matched_keywords[:6])
        reason_parts.append(f"keywords=[{kw_str}]")
    reason_parts.append(f"confidence={best.score:.2f}")

    alternatives = [c for c in top[1:] if c.score > 0]
    if alternatives:
        alt_str = ", ".join([f"{c.name}:{c.score:.2f}" for c in alternatives])
        reason_parts.append(f"alternatives=[{alt_str}]")

    reason = " | ".join(reason_parts)

    result = RoutingResult(
        selected=best.name,
        score=best.score,
        matched_keywords=best.matched_keywords,
        candidates=top,
        reason=reason,
        mode="auto"
    )

    logger.info(
        f"Explainable routing: selected={best.name}, "
        f"score={best.score:.2f}, "
        f"keywords={best.matched_keywords[:3]}"
    )

    return result


def answer_with_twin(
    twin: TwinAgent,
    org: Union[Dict[str, Any], OrgConfig],
    knowledge_snippets: str,
    question: str,
    llm_client: Optional[BaseLLMClient] = None
) -> str:
    """
    Digital Twin으로 답변 생성

    Args:
        twin: TwinAgent 인스턴스
        org: 조직 설정 (Dict 또는 OrgConfig Pydantic 모델)
        knowledge_snippets: 관련 지식 스니펫
        question: 사용자 질문
        llm_client: LLM 클라이언트 (없으면 글로벌 클라이언트 사용)

    Returns:
        답변 문자열
    """
    # OrgConfig를 Dict로 변환 (LLM 클라이언트 호환성)
    if isinstance(org, OrgConfig):
        org = org.model_dump()
    client = llm_client or _llm_client
    client_name = type(client).__name__

    logger.info(f"Generating answer: twin={twin.name}, client={client_name}")
    start_time = time.time()

    try:
        response = client.generate_response(twin, org, knowledge_snippets, question)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Answer generated: twin={twin.name}, duration={duration_ms:.2f}ms, length={len(response)}")
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Answer generation failed: twin={twin.name}, error={str(e)}, duration={duration_ms:.2f}ms")
        raise


def answer_with_citations(
    twin: TwinAgent,
    org: Union[Dict[str, Any], OrgConfig],
    knowledge_items: List[Dict[str, Any]],
    question: str,
    llm_client: Optional[BaseLLMClient] = None
) -> AnswerResult:
    """
    Digital Twin으로 답변 생성 + 인용 정보 포함 (ADR-106)

    Args:
        twin: TwinAgent 인스턴스
        org: 조직 설정 (Dict 또는 OrgConfig Pydantic 모델)
        knowledge_items: 지식 항목 리스트 (Dict 형태)
        question: 사용자 질문
        llm_client: LLM 클라이언트 (없으면 글로벌 클라이언트 사용)

    Returns:
        AnswerResult (답변 + 인용 정보)
    """
    # 1) 관련 지식 찾기 + 인용 생성
    citations, snippet_text = find_relevant_knowledge(question, knowledge_items)

    # 2) 답변 생성
    answer = answer_with_twin(twin, org, snippet_text, question, llm_client)

    # 3) 결과 조합
    result = AnswerResult(
        answer=answer,
        routed_to=twin.name,
        citations=citations
    )

    logger.info(
        f"Answer with citations: twin={twin.name}, "
        f"citations_count={len(citations)}, "
        f"answer_length={len(answer)}"
    )

    return result


def route_and_answer(
    twins: Dict[str, TwinAgent],
    org: Union[Dict[str, Any], OrgConfig],
    knowledge_items: List[Dict[str, Any]],
    question: str,
    llm_client: Optional[BaseLLMClient] = None
) -> AnswerResult:
    """
    질문 라우팅 + 답변 생성 통합 함수 (ADR-106)

    Args:
        twins: Twin 딕셔너리 (name -> TwinAgent)
        org: 조직 설정
        knowledge_items: 지식 항목 리스트
        question: 사용자 질문
        llm_client: LLM 클라이언트

    Returns:
        AnswerResult (답변 + 라우팅 정보 + 인용)
    """
    # 1) 라우팅
    routed_name = route_agent(question)
    twin = twins.get(routed_name)

    if twin is None:
        # Fallback to Jin Park (Backend)
        routed_name = "Jin Park"
        twin = twins.get(routed_name)
        logger.warning(f"Fallback to {routed_name} (twin not found)")

    # 2) 답변 + 인용 생성
    return answer_with_citations(twin, org, knowledge_items, question, llm_client)


# ============================================================
# ADR-110: Offline-first + LLM-enhanced 아키텍처
# ============================================================

def _format_citations_for_prompt(citations: List[Dict[str, Any]]) -> str:
    """
    HYBRID-003: 인용 정보를 LLM 프롬프트용 문자열로 변환

    Args:
        citations: 지식 항목 리스트

    Returns:
        Evidence 블록 문자열

    책임: 지식 항목을 구조화된 텍스트로 포맷팅 (SRP)
    """
    if not citations:
        return "(참고할 회사 지식 없음)"

    lines = []
    for i, cite in enumerate(citations, 1):
        source = cite.get("source", "unknown")
        tag = cite.get("tag", "unknown")
        text = cite.get("text", "")[:300]  # 최대 300자
        topic = cite.get("topic_hint", "")
        topic_str = f" [{topic}]" if topic else ""

        lines.append(f"[{i}] ({source}/{tag}{topic_str}) \"{text}\"")

    return "\n".join(lines)


def _validate_section_structure(
    llm_output: str,
    skeleton: StructuredAnswer
) -> bool:
    """
    HYBRID-004: LLM 출력이 스켈레톤 섹션 구조를 유지하는지 검증

    Args:
        llm_output: LLM이 생성한 응답
        skeleton: 원본 스켈레톤

    Returns:
        True if 섹션 구조 유지됨, False otherwise

    책임: 구조 검증만 담당 (SRP)
    """
    if not llm_output or len(llm_output) < 50:
        return False

    # 필수 섹션 헤더 체크 (최소 2개 이상)
    required_sections = [s.title for s in skeleton.sections[:3]]
    found_count = sum(1 for title in required_sections if title in llm_output)

    return found_count >= 2


def _enhance_with_llm(
    client: BaseLLMClient,
    twin: TwinAgent,
    org: Union[Dict[str, Any], OrgConfig],
    skeleton: StructuredAnswer,
    citations: List[Dict[str, Any]],
    question: str
) -> str:
    """
    HYBRID-002: 스켈레톤을 LLM으로 확장

    Args:
        client: LLM 클라이언트
        twin: TwinAgent 인스턴스
        org: 조직 설정
        skeleton: 오프라인 스켈레톤
        citations: 인용 항목
        question: 사용자 질문

    Returns:
        확장된 응답 문자열

    Raises:
        ValueError: 섹션 구조가 손상된 경우

    책임: LLM 확장 로직만 담당 (SRP)
    SOLID-OCP: 프롬프트 템플릿 변경으로 확장 가능
    """
    # OrgConfig를 Dict로 변환
    if isinstance(org, OrgConfig):
        org = org.model_dump()

    evidence_block = _format_citations_for_prompt(citations)
    skeleton_md = skeleton.to_markdown()

    system_prompt = f"""당신은 {twin.name} ({twin.role})의 Digital Twin입니다.

[중요 규칙 - 반드시 준수]
1. 아래 Draft의 섹션 구조(###)를 반드시 유지하세요
2. 섹션 헤더를 절대 변경하거나 생략하지 마세요
3. Evidence 블록의 내용만 인용하세요 (없는 내용 생성 금지)
4. 모르는 내용은 "추정" 또는 "확인 필요"로 명시하세요
5. 한국어로 답변하세요

[회사] {org.get('company', 'Veluga')}
[직무] {org.get('role', 'PM')}
[트윈 스타일] {twin.style}
"""

    user_prompt = f"""질문: {question}

Evidence (인용 가능한 회사 지식):
{evidence_block}

Draft (섹션 구조 유지 필수):
{skeleton_md}

위 Draft의 내용을 더 구체적이고 실용적으로 확장해주세요.
- 섹션 헤더(###)는 그대로 유지
- Evidence의 내용을 적절히 인용
- 추상적 내용을 구체적 예시로 보강
"""

    logger.debug(f"LLM enhancement: twin={twin.name}, evidence_count={len(citations)}")

    # temperature 낮게 설정 (구조 유지 우선)
    response = client.complete(
        system=system_prompt,
        user=user_prompt,
        temperature=0.2,
        max_tokens=1500
    )

    # 섹션 구조 검증
    if not _validate_section_structure(response, skeleton):
        logger.warning(f"LLM output missing required sections, fallback triggered")
        raise ValueError("LLM output missing required sections")

    return response


def generate_answer(
    question: str,
    org: Union[Dict[str, Any], OrgConfig],
    twin: TwinAgent,
    citations: List[Dict[str, Any]],
    llm_client: Optional[BaseLLMClient] = None,
    use_llm: bool = False,
) -> Dict[str, Any]:
    """
    HYBRID-001: Offline-first + LLM-enhanced 답변 생성 (ADR-110)

    핵심 원칙:
    1. 항상 오프라인 스켈레톤을 먼저 생성
    2. LLM은 스켈레톤을 확장/정교화만 수행
    3. LLM 실패 시 스켈레톤으로 즉시 폴백

    Args:
        question: 사용자 질문
        org: 조직 설정
        twin: TwinAgent 인스턴스
        citations: 인용할 지식 항목 리스트
        llm_client: LLM 클라이언트 (None이면 글로벌 클라이언트)
        use_llm: LLM 확장 사용 여부

    Returns:
        {
            "text": 최종 답변 문자열,
            "mode": "offline" | "llm",
            "structured": StructuredAnswer,
            "citations_used": List[Dict],
            "debug": {"fallback": ..., "provider": ...}
        }

    SOLID 원칙:
    - SRP: 답변 생성 오케스트레이션만 담당
    - OCP: 새 LLM provider 추가 시 확장 가능
    - DIP: BaseLLMClient 추상화에 의존
    """
    start_time = time.time()

    # Step 1: 오프라인 스켈레톤 생성 (항상 실행)
    evidence_text = _format_citations_for_prompt(citations)
    skeleton = render_twin_answer(twin, evidence_text)

    logger.info(
        f"Skeleton generated: twin={twin.name}, "
        f"sections={len(skeleton.sections)}, "
        f"citations={len(citations)}"
    )

    # Step 2: LLM 미사용 → 스켈레톤 반환
    client = llm_client or _llm_client
    is_mock = isinstance(client, MockLLMClient)

    if not use_llm or client is None or is_mock:
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Offline mode: twin={twin.name}, duration={duration_ms:.2f}ms")
        return {
            "text": skeleton.to_markdown(),
            "mode": "offline",
            "structured": skeleton,
            "citations_used": citations,
            "debug": {"reason": "llm_disabled" if not use_llm else "mock_client"}
        }

    # Step 3: LLM으로 스켈레톤 확장 시도
    try:
        enhanced = _enhance_with_llm(
            client, twin, org, skeleton, citations, question
        )
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"LLM enhanced: twin={twin.name}, "
            f"provider={type(client).__name__}, "
            f"duration={duration_ms:.2f}ms"
        )
        return {
            "text": enhanced,
            "mode": "llm",
            "structured": skeleton,
            "citations_used": citations,
            "debug": {"provider": type(client).__name__}
        }
    except Exception as e:
        # Step 4: 실패 시 폴백
        duration_ms = (time.time() - start_time) * 1000
        logger.warning(
            f"LLM enhancement failed, fallback to offline: "
            f"twin={twin.name}, error={type(e).__name__}: {str(e)}, "
            f"duration={duration_ms:.2f}ms"
        )
        return {
            "text": skeleton.to_markdown(),
            "mode": "offline",
            "structured": skeleton,
            "citations_used": citations,
            "debug": {"fallback": f"llm_error:{type(e).__name__}", "error_msg": str(e)[:100]}
        }
