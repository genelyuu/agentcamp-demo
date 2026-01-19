"""
pytest configuration and fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_question():
    """Sample question for routing tests"""
    return "고객 우선순위는 어떻게 정하나요?"


@pytest.fixture
def sample_submission():
    """Sample submission for review tests"""
    return """
    원인: API 타임아웃으로 인한 500 에러 발생
    재현조건: 동시 요청 100건 이상 시 발생
    재발방지: 커넥션 풀 사이즈 증가 및 타임아웃 설정 조정
    로그: ERROR 2026-01-19 connection_pool_exhausted
    """


@pytest.fixture
def mock_org_config():
    """Mock organization config"""
    return {
        "company": "Veluga",
        "role": "Backend Engineer",
        "tools": ["Slack", "GitHub"],
        "rubric": {
            "acceptance_keywords": ["원인", "재현", "재발방지", "로그"]
        }
    }
