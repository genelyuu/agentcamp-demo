"""
core/evaluation.py - 평가 모듈
ARCH-004: scoring.py → core/evaluation.py 마이그레이션
ADR-101: UI/Core Boundary Separation
ADR-103: Evaluation Gate
ADR-106: Citation Transparency - 키워드 매칭 근거 투명성
ADR-109: Structured Rubric Scoring - 4칸 구조 평가
LOG-003: 로깅 적용
ERR-TYPE-002: 타입 힌트 강화 (Dict → Union[Dict, OJTTask])
"""
import re
from typing import Any, Dict, List, Tuple, Union

from schemas import OJTTask, ReviewResult, KeywordMatch
from schemas.rubric import (
    ChecklistItem,
    RubricColumn,
    RubricReviewResult,
    calculate_grade,
    get_default_cause_items,
    get_default_reproduction_items,
    get_default_prevention_items,
    get_default_evidence_items,
)
from .logger import get_logger
from .citation import extract_keyword_context

logger = get_logger("evaluation")


def simple_review(
    task: Union[Dict[str, Any], OJTTask],
    submission: str
) -> Tuple[int, Dict[str, Any]]:
    """
    루브릭 기반 제출물 평가

    Args:
        task: 미션 정보 (Dict 또는 OJTTask Pydantic 모델)
        submission: 제출 내용

    Returns:
        (점수, 피드백 딕셔너리)
    """
    # OJTTask를 Dict로 변환
    if isinstance(task, OJTTask):
        task = {
            "title": task.title,
            "context": task.context,
            "deliverable": task.deliverable,
            "acceptance_keywords": task.acceptance_keywords
        }

    score = 50
    feedback: Dict[str, Any] = {
        "strengths": [],
        "improvements": [],
        "next_step": ""
    }

    # 키워드 매칭
    keywords = task.get("acceptance_keywords", [])
    hit_count = _count_keyword_hits(keywords, submission)

    # 점수 계산
    if keywords:
        keyword_score = int(50 * (hit_count / len(keywords)))
        score += keyword_score
    else:
        score += 20

    # 강점/개선점 판정
    _evaluate_strengths(feedback, keywords, hit_count)
    _evaluate_improvements(feedback, submission)

    # 다음 스텝 안내
    feedback["next_step"] = (
        "리뷰 반영 후 1회 재제출하거나, "
        "AI 멘토에게 '어떤 로그를 봐야 하나'를 질문해보세요."
    )

    final_score = min(100, score)
    logger.info(
        f"Review completed: score={final_score}, "
        f"keywords_hit={hit_count}/{len(keywords)}, "
        f"submission_len={len(submission)}"
    )

    return final_score, feedback


def review_with_task(task: OJTTask, submission: str) -> Tuple[int, Dict[str, Any]]:
    """
    OJTTask Pydantic 모델 기반 평가

    Args:
        task: OJTTask 인스턴스
        submission: 제출 내용

    Returns:
        (점수, 피드백 딕셔너리)
    """
    task_dict = {
        "title": task.title,
        "context": task.context,
        "deliverable": task.deliverable,
        "acceptance_keywords": task.acceptance_keywords
    }
    return simple_review(task_dict, submission)


def _count_keyword_hits(keywords: list, submission: str) -> int:
    """키워드 포함 횟수 계산"""
    lower_submission = submission.lower()
    return sum(1 for kw in keywords if kw.lower() in lower_submission)


def _evaluate_strengths(feedback: Dict[str, Any], keywords: list, hit_count: int) -> None:
    """강점 평가"""
    threshold = max(1, len(keywords) // 2)
    if hit_count >= threshold:
        feedback["strengths"].append("핵심 포인트를 일부 포함했습니다.")


def _evaluate_improvements(feedback: Dict[str, Any], submission: str) -> None:
    """개선점 평가"""
    if len(submission) < 120:
        feedback["improvements"].append(
            "설명이 너무 짧습니다. 근거(로그/수치/재현 조건)를 추가하세요."
        )

    # 키워드 미포함 시 기본 개선점
    if not feedback.get("strengths"):
        feedback["improvements"].append(
            "완료 기준 키워드(원인/재발방지/재현조건 등)를 더 명시하세요."
        )


def _build_keyword_matches(
    keywords: List[str],
    submission: str
) -> List[KeywordMatch]:
    """
    키워드 매칭 상세 결과 생성 (ADR-106)

    Args:
        keywords: 평가 키워드 리스트
        submission: 제출 내용

    Returns:
        KeywordMatch 리스트
    """
    matches: List[KeywordMatch] = []
    lower_submission = submission.lower()

    for kw in keywords:
        matched = kw.lower() in lower_submission
        context = None

        if matched:
            context = extract_keyword_context(submission, kw, context_chars=40)

        matches.append(KeywordMatch(
            keyword=kw,
            matched=matched,
            context=context
        ))

    return matches


def review_with_evidence(
    task: Union[Dict[str, Any], OJTTask],
    submission: str
) -> ReviewResult:
    """
    루브릭 기반 제출물 평가 + 키워드 매칭 근거 포함 (ADR-106)

    Args:
        task: 미션 정보 (Dict 또는 OJTTask Pydantic 모델)
        submission: 제출 내용

    Returns:
        ReviewResult (점수 + 피드백 + 키워드 매칭 근거)
    """
    # OJTTask를 Dict로 변환
    if isinstance(task, OJTTask):
        task = {
            "title": task.title,
            "context": task.context,
            "deliverable": task.deliverable,
            "acceptance_keywords": task.acceptance_keywords
        }

    keywords = task.get("acceptance_keywords", [])

    # 키워드 매칭 상세 결과 생성
    keyword_matches = _build_keyword_matches(keywords, submission)
    hit_count = sum(1 for km in keyword_matches if km.matched)

    # 점수 계산
    score = 50
    if keywords:
        keyword_score = int(50 * (hit_count / len(keywords)))
        score += keyword_score
    else:
        score += 20

    # 강점/개선점 판정
    strengths: List[str] = []
    improvements: List[str] = []

    threshold = max(1, len(keywords) // 2)
    if hit_count >= threshold:
        strengths.append("핵심 포인트를 일부 포함했습니다.")

        # 매칭된 키워드 명시
        matched_kws = [km.keyword for km in keyword_matches if km.matched]
        if matched_kws:
            strengths.append(f"포함된 키워드: {', '.join(matched_kws)}")

    if len(submission) < 120:
        improvements.append(
            "설명이 너무 짧습니다. 근거(로그/수치/재현 조건)를 추가하세요."
        )

    if not strengths:
        improvements.append(
            "완료 기준 키워드(원인/재발방지/재현조건 등)를 더 명시하세요."
        )

        # 누락된 키워드 명시
        missed_kws = [km.keyword for km in keyword_matches if not km.matched]
        if missed_kws:
            improvements.append(f"누락된 키워드: {', '.join(missed_kws)}")

    final_score = min(100, score)

    result = ReviewResult(
        score=final_score,
        strengths=strengths,
        improvements=improvements,
        next_step=(
            "리뷰 반영 후 1회 재제출하거나, "
            "AI 멘토에게 '어떤 로그를 봐야 하나'를 질문해보세요."
        ),
        keyword_matches=keyword_matches
    )

    logger.info(
        f"Review with evidence: score={final_score}, "
        f"keywords_hit={hit_count}/{len(keywords)}, "
        f"submission_len={len(submission)}"
    )

    return result


# ============================================================
# 4칸 구조 루브릭 평가 (ADR-109)
# ============================================================

# 칸별 키워드 패턴 정의
_CAUSE_PATTERNS = [
    r"원인|root\s*cause|why|이유|근본|문제.*발생",
    r"때문|인해|으로\s*인한|원인.*분석",
    r"버그|에러|오류|장애.*원인",
]

_REPRODUCTION_PATTERNS = [
    r"재현|reproduce|repro|steps?\s*to|절차|순서",
    r"환경|조건|설정|config|setup",
    r"1\.|2\.|3\.|step\s*\d|단계",
]

_PREVENTION_PATTERNS = [
    r"재발\s*방지|prevent|hotfix|permanent|개선|수정|fix",
    r"모니터링|알림|alert|notification",
    r"대응|조치|해결.*방안|solution",
]

_EVIDENCE_PATTERNS = [
    r"로그|log|스크린샷|screenshot|증거|evidence",
    r"메트릭|metric|수치|데이터|통계",
    r"타임라인|timeline|언제|시간|datetime|\d{4}[-/]\d{2}",
]


def _check_pattern_match(text: str, patterns: List[str]) -> bool:
    """패턴 매칭 여부 확인"""
    lower_text = text.lower()
    for pattern in patterns:
        if re.search(pattern, lower_text, re.IGNORECASE):
            return True
    return False


def _evaluate_column(
    submission: str,
    items: List[ChecklistItem],
    patterns: List[str],
    column_name: str
) -> Tuple[List[ChecklistItem], int, List[str]]:
    """
    개별 칸 평가

    Returns:
        (체크리스트 항목들, 점수, 피드백 리스트)
    """
    lower_submission = submission.lower()
    checked_items: List[ChecklistItem] = []
    feedbacks: List[str] = []
    checked_count = 0

    for item in items:
        # 간단한 휴리스틱: 패턴 존재 여부로 체크
        # 더 정교한 구현은 LLM 기반 평가로 확장 가능
        is_checked = _check_pattern_match(submission, patterns)

        if is_checked:
            checked_count += 1
            feedback = f"✅ {item.label}"
        else:
            feedback = f"❌ {item.label} - 해당 내용이 부족합니다"
            feedbacks.append(item.label)

        checked_items.append(ChecklistItem(
            id=item.id,
            label=item.label,
            checked=is_checked,
            feedback=feedback
        ))

    # 점수 계산 (각 칸 25점 만점)
    if items:
        score = int(25 * (checked_count / len(items)))
    else:
        score = 0

    return checked_items, score, feedbacks


def _validate_submission_structure(submission: str) -> Tuple[bool, List[str]]:
    """
    제출물 구조 검증 (키워드 게이밍 방지)

    Returns:
        (유효 여부, 경고 메시지 리스트)
    """
    warnings: List[str] = []
    is_valid = True

    # 최소 길이 검증
    if len(submission) < 100:
        warnings.append("제출물이 너무 짧습니다 (최소 100자 권장)")
        is_valid = False

    # 문장 구조 검증 (단순 키워드 나열 방지)
    sentences = re.split(r'[.!?。]', submission)
    valid_sentences = [s for s in sentences if len(s.strip()) > 10]
    if len(valid_sentences) < 3:
        warnings.append("완전한 문장이 부족합니다 (최소 3문장 권장)")
        is_valid = False

    # 섹션/구조 검증
    has_structure = any([
        re.search(r'#+\s', submission),  # 마크다운 헤더
        re.search(r'\d+\.\s', submission),  # 번호 리스트
        re.search(r'[-*]\s', submission),  # 불릿 리스트
    ])
    if not has_structure:
        warnings.append("구조화된 포맷(헤더, 리스트 등)을 사용하면 더 좋습니다")

    return is_valid, warnings


def rubric_review(submission: str) -> RubricReviewResult:
    """
    4칸 구조 루브릭 평가 (ADR-109)

    4개 칸:
    - 원인 분석 (Cause): 25점
    - 재현 방법 (Reproduction): 25점
    - 재발 방지 (Prevention): 25점
    - 증거 (Evidence): 25점

    Args:
        submission: 제출 내용

    Returns:
        RubricReviewResult: 4칸 평가 결과
    """
    # 구조 검증
    is_valid, structure_warnings = _validate_submission_structure(submission)

    # 원인 분석 칸 평가
    cause_items, cause_score, cause_missing = _evaluate_column(
        submission,
        get_default_cause_items(),
        _CAUSE_PATTERNS,
        "cause"
    )

    # 재현 방법 칸 평가
    repro_items, repro_score, repro_missing = _evaluate_column(
        submission,
        get_default_reproduction_items(),
        _REPRODUCTION_PATTERNS,
        "reproduction"
    )

    # 재발 방지 칸 평가
    prev_items, prev_score, prev_missing = _evaluate_column(
        submission,
        get_default_prevention_items(),
        _PREVENTION_PATTERNS,
        "prevention"
    )

    # 증거 칸 평가
    evid_items, evid_score, evid_missing = _evaluate_column(
        submission,
        get_default_evidence_items(),
        _EVIDENCE_PATTERNS,
        "evidence"
    )

    # 총점 계산
    total_score = cause_score + repro_score + prev_score + evid_score

    # 구조 검증 실패 시 페널티
    if not is_valid:
        total_score = max(0, total_score - 10)

    grade = calculate_grade(total_score)

    # 누락된 요소 집계
    missing_elements = []
    if cause_missing:
        missing_elements.append(f"원인 분석: {', '.join(cause_missing[:2])}")
    if repro_missing:
        missing_elements.append(f"재현 방법: {', '.join(repro_missing[:2])}")
    if prev_missing:
        missing_elements.append(f"재발 방지: {', '.join(prev_missing[:2])}")
    if evid_missing:
        missing_elements.append(f"증거: {', '.join(evid_missing[:2])}")
    missing_elements.extend(structure_warnings)

    # 종합 피드백 생성
    if grade in ["A", "B"]:
        overall_feedback = "잘 작성된 보고서입니다. 구조와 내용이 충실합니다."
    elif grade == "C":
        overall_feedback = "기본적인 내용은 포함되어 있으나, 일부 항목이 부족합니다."
    elif grade == "D":
        overall_feedback = "여러 항목이 누락되어 있습니다. 체크리스트를 참고하여 보완하세요."
    else:
        overall_feedback = "대부분의 필수 항목이 누락되어 있습니다. 4칸 구조에 맞춰 다시 작성하세요."

    result = RubricReviewResult(
        cause=RubricColumn(
            name="cause",
            display_name="원인 분석",
            score=cause_score,
            items=cause_items,
            summary=f"원인 분석 섹션: {cause_score}/25점"
        ),
        reproduction=RubricColumn(
            name="reproduction",
            display_name="재현 방법",
            score=repro_score,
            items=repro_items,
            summary=f"재현 방법 섹션: {repro_score}/25점"
        ),
        prevention=RubricColumn(
            name="prevention",
            display_name="재발 방지",
            score=prev_score,
            items=prev_items,
            summary=f"재발 방지 섹션: {prev_score}/25점"
        ),
        evidence=RubricColumn(
            name="evidence",
            display_name="증거",
            score=evid_score,
            items=evid_items,
            summary=f"증거 섹션: {evid_score}/25점"
        ),
        total_score=total_score,
        grade=grade,
        overall_feedback=overall_feedback,
        missing_elements=missing_elements
    )

    logger.info(
        f"Rubric review: total={total_score}, grade={grade}, "
        f"cause={cause_score}, repro={repro_score}, "
        f"prev={prev_score}, evid={evid_score}"
    )

    return result
