"""
core/evaluation.py - 평가 모듈
ARCH-004: scoring.py → core/evaluation.py 마이그레이션
ADR-101: UI/Core Boundary Separation
ADR-103: Evaluation Gate
LOG-003: 로깅 적용
"""
from typing import Any, Dict, Tuple

from schemas import OJTTask
from .logger import get_logger

logger = get_logger("evaluation")


def simple_review(task: Dict[str, Any], submission: str) -> Tuple[int, Dict[str, Any]]:
    """
    루브릭 기반 제출물 평가

    Args:
        task: 미션 정보 (acceptance_keywords 포함)
        submission: 제출 내용

    Returns:
        (점수, 피드백 딕셔너리)
    """
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
