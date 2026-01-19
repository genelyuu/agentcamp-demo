"""
tests/unit/test_evaluation.py - Evaluation 모듈 단위 테스트
TEST-004: 평가 로직 테스트
"""
import pytest

from core.evaluation import (
    simple_review,
    review_with_task,
    _count_keyword_hits,
    _evaluate_strengths,
    _evaluate_improvements,
)
from schemas import OJTTask


class TestSimpleReview:
    """simple_review 함수 테스트"""

    def test_returns_tuple(self):
        """simple_review가 (점수, 피드백) 튜플을 반환하는지 테스트"""
        task = {"acceptance_keywords": ["원인", "로그"]}
        submission = "원인을 분석했습니다."

        result = simple_review(task, submission)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_score_is_integer(self):
        """점수가 정수인지 테스트"""
        task = {"acceptance_keywords": ["원인"]}
        submission = "테스트 제출"

        score, _ = simple_review(task, submission)

        assert isinstance(score, int)

    def test_score_range(self):
        """점수가 0-100 범위인지 테스트"""
        task = {"acceptance_keywords": ["원인", "로그", "재현"]}
        submission = "원인 로그 재현 모두 포함"

        score, _ = simple_review(task, submission)

        assert 0 <= score <= 100

    def test_feedback_structure(self):
        """피드백 구조가 올바른지 테스트"""
        task = {"acceptance_keywords": ["원인"]}
        submission = "테스트"

        _, feedback = simple_review(task, submission)

        assert "strengths" in feedback
        assert "improvements" in feedback
        assert "next_step" in feedback
        assert isinstance(feedback["strengths"], list)
        assert isinstance(feedback["improvements"], list)

    def test_keyword_matching_increases_score(self):
        """키워드 매칭 시 점수가 증가하는지 테스트"""
        task = {"acceptance_keywords": ["원인", "로그"]}

        score_without, _ = simple_review(task, "아무 내용 없음")
        score_with, _ = simple_review(task, "원인을 분석하고 로그를 확인함")

        assert score_with > score_without

    def test_empty_keywords_gives_base_score(self):
        """키워드가 없으면 기본 점수를 부여하는지 테스트"""
        task = {"acceptance_keywords": []}
        submission = "테스트 제출"

        score, _ = simple_review(task, submission)

        # 기본 50 + 20 = 70 (키워드 없을 때)
        assert score >= 70

    def test_short_submission_gets_improvement(self):
        """짧은 제출물에 개선점이 추가되는지 테스트"""
        task = {"acceptance_keywords": ["원인"]}
        short_submission = "짧음"  # 120자 미만

        _, feedback = simple_review(task, short_submission)

        # 개선점에 짧은 설명 관련 피드백이 있어야 함
        assert len(feedback["improvements"]) > 0


class TestReviewWithTask:
    """review_with_task 함수 테스트"""

    def test_accepts_ojt_task(self):
        """OJTTask 모델을 인자로 받는지 테스트"""
        task = OJTTask(
            id="test-001",
            title="테스트 미션",
            context="테스트 컨텍스트",
            deliverable="테스트 산출물",
            acceptance_keywords=["원인", "로그"]
        )
        submission = "원인을 파악했습니다."

        score, feedback = review_with_task(task, submission)

        assert isinstance(score, int)
        assert isinstance(feedback, dict)

    def test_uses_task_keywords(self):
        """OJTTask의 acceptance_keywords를 사용하는지 테스트"""
        task = OJTTask(
            id="test-002",
            title="키워드 테스트",
            context="컨텍스트",
            deliverable="산출물",
            acceptance_keywords=["특별키워드"]
        )

        score_with, _ = review_with_task(task, "특별키워드를 포함한 제출")
        score_without, _ = review_with_task(task, "키워드 없는 제출")

        assert score_with > score_without


class TestHelperFunctions:
    """헬퍼 함수 테스트"""

    def test_count_keyword_hits_basic(self):
        """_count_keyword_hits 기본 동작 테스트"""
        keywords = ["원인", "로그", "재현"]
        submission = "원인을 파악하고 로그를 확인했습니다."

        count = _count_keyword_hits(keywords, submission)

        assert count == 2  # 원인, 로그

    def test_count_keyword_hits_case_insensitive(self):
        """대소문자 구분 없이 카운트하는지 테스트"""
        keywords = ["ERROR", "log"]
        submission = "error가 발생했고 LOG를 확인함"

        count = _count_keyword_hits(keywords, submission)

        assert count == 2

    def test_count_keyword_hits_empty(self):
        """키워드가 없을 때 0을 반환하는지 테스트"""
        keywords = []
        submission = "아무 내용"

        count = _count_keyword_hits(keywords, submission)

        assert count == 0

    def test_evaluate_strengths_adds_when_threshold_met(self):
        """임계값 충족 시 강점이 추가되는지 테스트"""
        feedback = {"strengths": [], "improvements": []}
        keywords = ["원인", "로그"]
        hit_count = 1  # 2개 중 1개 = 50%, threshold = max(1, 1) = 1

        _evaluate_strengths(feedback, keywords, hit_count)

        assert len(feedback["strengths"]) > 0

    def test_evaluate_improvements_for_short_text(self):
        """짧은 텍스트에 개선점이 추가되는지 테스트"""
        feedback = {"strengths": [], "improvements": []}
        short_submission = "짧음"

        _evaluate_improvements(feedback, short_submission)

        assert len(feedback["improvements"]) > 0
