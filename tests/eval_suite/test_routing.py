"""
tests/eval_suite/test_routing.py - 라우팅 평가 테스트
EVAL-003: 질문 → 올바른 Twin 매핑 테스트
ADR-103: Evaluation Gate
"""
import json
import pytest
from pathlib import Path

from core.llm import create_router, MockRouter


# Golden Set 로드
GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


@pytest.fixture
def golden_set():
    """Golden Set 로드"""
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def router():
    """Mock Router 인스턴스"""
    return create_router()


class TestRouting:
    """라우팅 정확도 테스트"""

    @pytest.mark.eval
    def test_routing_accuracy(self, golden_set, router):
        """전체 라우팅 정확도 테스트 (90%+ 목표)"""
        cases = golden_set["routing_cases"]
        correct = 0
        results = []

        for case in cases:
            question = case["question"]
            expected = case["expected_twin"]
            actual = router.route(question)

            is_correct = actual == expected
            if is_correct:
                correct += 1

            results.append({
                "id": case["id"],
                "question": question[:30] + "...",
                "expected": expected,
                "actual": actual,
                "correct": is_correct
            })

        accuracy = correct / len(cases) * 100
        print(f"\n라우팅 정확도: {accuracy:.1f}% ({correct}/{len(cases)})")

        for r in results:
            status = "✓" if r["correct"] else "✗"
            print(f"  {status} {r['id']}: {r['actual']} (expected: {r['expected']})")

        assert accuracy >= 90.0, f"라우팅 정확도 {accuracy:.1f}% < 90% 목표"

    @pytest.mark.eval
    @pytest.mark.parametrize("twin,keywords", [
        ("Sam Lee", ["우선순위", "전략", "고객", "리스크", "비용"]),
        ("JH Kim", ["요구사항", "스코프", "정의", "kpi", "지표"]),
        ("Seul Kim", ["ui", "ux", "화면", "프론트", "component"]),
    ])
    def test_keyword_routing(self, router, twin, keywords):
        """키워드별 라우팅 테스트"""
        for keyword in keywords:
            question = f"{keyword}에 대해 알려주세요"
            result = router.route(question)
            assert result == twin, f"'{keyword}' → {result} (expected: {twin})"

    @pytest.mark.eval
    def test_default_routing(self, router):
        """기본 라우팅 (Jin Park) 테스트"""
        questions = [
            "API 설계해주세요",
            "서버 로그 확인 방법",
            "데이터베이스 연결 오류",
            "이건 뭔가요?",  # 키워드 없음
        ]

        for question in questions:
            result = router.route(question)
            assert result == "Jin Park", f"'{question}' → {result} (expected: Jin Park)"

    @pytest.mark.eval
    def test_router_protocol_compliance(self, router):
        """Router Protocol 준수 테스트"""
        from core.llm import RouterCapability

        # Protocol 검증
        assert isinstance(router, RouterCapability), "Router must implement RouterCapability"

        # route 메서드 존재 및 반환 타입
        result = router.route("테스트 질문")
        assert isinstance(result, str), "route() must return str"

        # 유효한 Twin 이름 반환
        valid_twins = ["Sam Lee", "JH Kim", "Seul Kim", "Jin Park"]
        assert result in valid_twins, f"Invalid twin name: {result}"
