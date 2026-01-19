"""
tests/eval_suite/test_review.py - 평가 테스트
EVAL-004: 제출 → 점수 범위 검증 테스트
ADR-103: Evaluation Gate
"""
import json
import pytest
from pathlib import Path

from core.llm import create_judge, MockJudge
from schemas import OJTTask


# Golden Set 로드
GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


@pytest.fixture
def golden_set():
    """Golden Set 로드"""
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def judge():
    """Mock Judge 인스턴스"""
    return create_judge()


class TestReview:
    """평가 로직 테스트"""

    @pytest.mark.eval
    def test_review_score_correlation(self, golden_set, judge):
        """점수 범위 검증 테스트"""
        cases = golden_set["review_cases"]
        in_range = 0
        results = []

        for case in cases:
            task_data = case["task"]
            task = OJTTask(
                title=task_data["title"],
                context=task_data["context"],
                deliverable=task_data["deliverable"],
                acceptance_keywords=task_data["acceptance_keywords"]
            )

            result = judge.judge(task, case["submission"])
            score = result["score"]

            expected_min = case["expected_score_min"]
            expected_max = case["expected_score_max"]
            is_in_range = expected_min <= score <= expected_max

            if is_in_range:
                in_range += 1

            results.append({
                "id": case["id"],
                "score": score,
                "expected_range": f"{expected_min}-{expected_max}",
                "in_range": is_in_range
            })

        accuracy = in_range / len(cases) * 100
        print(f"\n점수 범위 정확도: {accuracy:.1f}% ({in_range}/{len(cases)})")

        for r in results:
            status = "✓" if r["in_range"] else "✗"
            print(f"  {status} {r['id']}: {r['score']} (expected: {r['expected_range']})")

        assert accuracy >= 70.0, f"점수 상관관계 {accuracy:.1f}% < 70% 목표"

    @pytest.mark.eval
    def test_review_feedback_structure(self, judge):
        """피드백 구조 테스트"""
        task = OJTTask(
            title="테스트 미션",
            context="테스트 상황",
            deliverable="테스트 제출물",
            acceptance_keywords=["키워드1", "키워드2"]
        )

        result = judge.judge(task, "키워드1이 포함된 제출물입니다.")

        # 필수 키 확인
        assert "score" in result, "score 필드 누락"
        assert "strengths" in result, "strengths 필드 누락"
        assert "improvements" in result, "improvements 필드 누락"
        assert "next_step" in result, "next_step 필드 누락"

        # 타입 확인
        assert isinstance(result["score"], int), "score must be int"
        assert isinstance(result["strengths"], list), "strengths must be list"
        assert isinstance(result["improvements"], list), "improvements must be list"
        assert isinstance(result["next_step"], str), "next_step must be str"

        # 점수 범위 확인
        assert 0 <= result["score"] <= 100, f"score {result['score']} out of range"

    @pytest.mark.eval
    def test_review_keyword_scoring(self, judge):
        """키워드 점수 반영 테스트"""
        task = OJTTask(
            title="테스트",
            context="테스트",
            deliverable="테스트",
            acceptance_keywords=["원인", "재현", "재발방지", "로그"]
        )

        # 키워드 0개
        result_0 = judge.judge(task, "아무 내용 없는 제출물입니다.")
        # 키워드 2개
        result_2 = judge.judge(task, "원인은 버그입니다. 로그를 확인했습니다.")
        # 키워드 4개
        result_4 = judge.judge(task, "원인은 버그입니다. 재현 가능합니다. 재발방지 조치했습니다. 로그 첨부합니다.")

        print(f"\n키워드 점수: 0개={result_0['score']}, 2개={result_2['score']}, 4개={result_4['score']}")

        # 키워드가 많을수록 점수가 높아야 함
        assert result_0["score"] <= result_2["score"], "더 많은 키워드 → 더 높은 점수"
        assert result_2["score"] <= result_4["score"], "더 많은 키워드 → 더 높은 점수"

    @pytest.mark.eval
    def test_judge_protocol_compliance(self, judge):
        """Judge Protocol 준수 테스트"""
        from core.llm import JudgeCapability

        # Protocol 검증
        assert isinstance(judge, JudgeCapability), "Judge must implement JudgeCapability"

        task = OJTTask(
            title="테스트",
            context="테스트",
            deliverable="테스트",
            acceptance_keywords=[]
        )

        # judge 메서드 존재 및 반환 타입
        result = judge.judge(task, "테스트 제출물")
        assert isinstance(result, dict), "judge() must return dict"
