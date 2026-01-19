"""
tests/eval_suite/runner.py - Eval Gate 통합 러너
EVAL-006: 전체 Eval Suite 실행 및 결과 집계
ADR-103: Evaluation Gate
"""
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class EvalResult:
    """개별 테스트 결과"""
    name: str
    passed: int
    failed: int
    total: int
    duration: float
    details: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0

    @property
    def status(self) -> str:
        if self.failed == 0:
            return "PASS"
        elif self.success_rate >= 70:
            return "WARN"
        else:
            return "FAIL"


@dataclass
class EvalSummary:
    """Eval Gate 전체 요약"""
    timestamp: str
    results: List[EvalResult]
    overall_status: str = "UNKNOWN"

    def __post_init__(self):
        self.overall_status = self._calculate_overall_status()

    def _calculate_overall_status(self) -> str:
        if not self.results:
            return "UNKNOWN"

        statuses = [r.status for r in self.results]

        # 하나라도 FAIL이면 전체 FAIL
        if "FAIL" in statuses:
            return "FAIL"
        # 하나라도 WARN이면 전체 WARN
        if "WARN" in statuses:
            return "WARN"
        return "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_status": self.overall_status,
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "passed": r.passed,
                    "failed": r.failed,
                    "total": r.total,
                    "success_rate": f"{r.success_rate:.1f}%",
                    "duration": f"{r.duration:.2f}s"
                }
                for r in self.results
            ]
        }


class EvalGateRunner:
    """Eval Gate 러너"""

    def __init__(self, eval_suite_path: Path = None):
        self.eval_suite_path = eval_suite_path or Path(__file__).parent
        self.results: List[EvalResult] = []

    def run_test(self, test_file: str) -> EvalResult:
        """개별 테스트 파일 실행"""
        test_path = self.eval_suite_path / test_file

        start_time = datetime.now()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short", "-m", "eval"],
            capture_output=True,
            text=True,
            cwd=str(self.eval_suite_path.parent.parent)  # 프로젝트 루트
        )
        duration = (datetime.now() - start_time).total_seconds()

        # pytest 출력 파싱
        output = result.stdout + result.stderr
        passed, failed, total = self._parse_pytest_output(output)

        return EvalResult(
            name=test_file.replace("test_", "").replace(".py", ""),
            passed=passed,
            failed=failed,
            total=total,
            duration=duration,
            details=[{"output": output}]
        )

    def _parse_pytest_output(self, output: str) -> tuple:
        """pytest 출력에서 결과 파싱"""
        import re

        # "X passed, Y failed" 패턴 찾기
        passed = failed = 0

        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))

        total = passed + failed
        return passed, failed, total

    def run_all(self) -> EvalSummary:
        """전체 Eval Suite 실행"""
        test_files = [
            "test_routing.py",
            "test_review.py",
            "test_safety.py",
        ]

        self.results = []
        for test_file in test_files:
            result = self.run_test(test_file)
            self.results.append(result)
            print(f"[{result.status}] {result.name}: {result.passed}/{result.total} ({result.success_rate:.1f}%)")

        summary = EvalSummary(
            timestamp=datetime.now().isoformat(),
            results=self.results
        )

        return summary

    def generate_report(self, summary: EvalSummary, output_path: Path = None) -> str:
        """마크다운 리포트 생성"""
        report = []

        # 헤더
        report.append("# Eval Gate Report")
        report.append(f"\n**Timestamp:** {summary.timestamp}")
        report.append(f"**Overall Status:** {self._status_badge(summary.overall_status)}")
        report.append("")

        # 요약 테이블
        report.append("## Summary")
        report.append("")
        report.append("| Test | Status | Passed | Failed | Rate | Duration |")
        report.append("|------|--------|--------|--------|------|----------|")

        for r in summary.results:
            status_badge = self._status_badge(r.status)
            report.append(f"| {r.name} | {status_badge} | {r.passed} | {r.failed} | {r.success_rate:.1f}% | {r.duration:.2f}s |")

        report.append("")

        # 상세 결과
        report.append("## Details")
        report.append("")

        for r in summary.results:
            report.append(f"### {r.name}")
            report.append(f"- Status: {self._status_badge(r.status)}")
            report.append(f"- Tests: {r.passed}/{r.total} passed")
            report.append("")

        # 결론
        report.append("## Conclusion")
        report.append("")

        if summary.overall_status == "PASS":
            report.append("✅ All evaluation gates passed. Safe to deploy.")
        elif summary.overall_status == "WARN":
            report.append("⚠️ Some tests have warnings. Review before deploying.")
        else:
            report.append("❌ Evaluation gates failed. Do not deploy.")

        report_text = "\n".join(report)

        if output_path:
            output_path.write_text(report_text, encoding="utf-8")

        return report_text

    def _status_badge(self, status: str) -> str:
        """상태 뱃지 생성"""
        badges = {
            "PASS": "✅ PASS",
            "WARN": "⚠️ WARN",
            "FAIL": "❌ FAIL",
            "UNKNOWN": "❓ UNKNOWN"
        }
        return badges.get(status, status)


def main():
    """CLI 엔트리포인트"""
    runner = EvalGateRunner()

    print("=" * 50)
    print("Eval Gate Runner")
    print("=" * 50)
    print("")

    summary = runner.run_all()

    print("")
    print("=" * 50)
    print(f"Overall Status: {summary.overall_status}")
    print("=" * 50)

    # 리포트 생성
    report = runner.generate_report(summary)
    print("\n" + report)

    # 종료 코드
    if summary.overall_status == "FAIL":
        sys.exit(1)
    elif summary.overall_status == "WARN":
        sys.exit(0)  # 경고는 통과
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
