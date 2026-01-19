"""
scoring.py - 리뷰 점수 모듈 (Backward Compatibility Wrapper)
ARCH-007: 기존 모듈 래퍼 유지
참조: core/evaluation.py
"""
from core.evaluation import simple_review

__all__ = ["simple_review"]
