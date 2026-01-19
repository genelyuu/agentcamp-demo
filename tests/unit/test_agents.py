"""
tests/unit/test_agents.py - Digital Twin Agents 단위 테스트
TEST-014: agents.py 테스트
"""
import pytest

from agents import TwinAgent, get_twins


class TestTwinAgent:
    """TwinAgent 데이터클래스 테스트"""

    def test_twin_agent_creation(self):
        """TwinAgent 생성 테스트"""
        agent = TwinAgent(
            name="Test Agent",
            role="Tester",
            style="직접적이고 명확함",
            responsibilities=["테스트", "검증"],
            decision_rules=["규칙1", "규칙2"]
        )
        assert agent.name == "Test Agent"
        assert agent.role == "Tester"
        assert agent.style == "직접적이고 명확함"
        assert len(agent.responsibilities) == 2
        assert len(agent.decision_rules) == 2

    def test_twin_agent_has_required_fields(self):
        """TwinAgent 필수 필드 테스트"""
        agent = TwinAgent(
            name="Test",
            role="Test Role",
            style="Test Style",
            responsibilities=[],
            decision_rules=[]
        )
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'role')
        assert hasattr(agent, 'style')
        assert hasattr(agent, 'responsibilities')
        assert hasattr(agent, 'decision_rules')


class TestGetTwins:
    """get_twins 함수 테스트"""

    @pytest.fixture
    def twins(self):
        """트윈 딕셔너리 픽스처"""
        return get_twins()

    def test_get_twins_returns_dict(self, twins):
        """get_twins가 딕셔너리 반환 테스트"""
        assert isinstance(twins, dict)

    def test_get_twins_has_four_twins(self, twins):
        """4명의 트윈이 있는지 테스트"""
        assert len(twins) == 4

    def test_get_twins_has_sam_lee(self, twins):
        """Sam Lee 트윈 존재 테스트"""
        assert "Sam Lee" in twins
        sam = twins["Sam Lee"]
        assert sam.name == "Sam Lee"
        assert sam.role == "CEO/대표"

    def test_get_twins_has_jh_kim(self, twins):
        """JH Kim 트윈 존재 테스트"""
        assert "JH Kim" in twins
        jh = twins["JH Kim"]
        assert jh.name == "JH Kim"
        assert jh.role == "PM"

    def test_get_twins_has_seul_kim(self, twins):
        """Seul Kim 트윈 존재 테스트"""
        assert "Seul Kim" in twins
        seul = twins["Seul Kim"]
        assert seul.name == "Seul Kim"
        assert seul.role == "Frontend"

    def test_get_twins_has_jin_park(self, twins):
        """Jin Park 트윈 존재 테스트"""
        assert "Jin Park" in twins
        jin = twins["Jin Park"]
        assert jin.name == "Jin Park"
        assert jin.role == "Backend"

    def test_twins_are_twin_agent_instances(self, twins):
        """모든 트윈이 TwinAgent 인스턴스인지 테스트"""
        for name, agent in twins.items():
            assert isinstance(agent, TwinAgent), f"{name} is not TwinAgent instance"

    def test_all_twins_have_responsibilities(self, twins):
        """모든 트윈이 responsibilities를 가지는지 테스트"""
        for name, agent in twins.items():
            assert len(agent.responsibilities) > 0, f"{name} has no responsibilities"

    def test_all_twins_have_decision_rules(self, twins):
        """모든 트윈이 decision_rules를 가지는지 테스트"""
        for name, agent in twins.items():
            assert len(agent.decision_rules) > 0, f"{name} has no decision_rules"

    def test_all_twins_have_style(self, twins):
        """모든 트윈이 style을 가지는지 테스트"""
        for name, agent in twins.items():
            assert agent.style is not None and len(agent.style) > 0, f"{name} has no style"


class TestTwinRoles:
    """트윈 역할별 테스트"""

    @pytest.fixture
    def twins(self):
        return get_twins()

    def test_sam_lee_is_ceo(self, twins):
        """Sam Lee CEO 역할 테스트"""
        sam = twins["Sam Lee"]
        assert "CEO" in sam.role or "대표" in sam.role
        # CEO는 전략, 고객, 리스크 관련 책임을 가져야 함
        responsibilities_str = " ".join(sam.responsibilities)
        assert "전략" in responsibilities_str or "우선순위" in responsibilities_str

    def test_jh_kim_is_pm(self, twins):
        """JH Kim PM 역할 테스트"""
        jh = twins["JH Kim"]
        assert "PM" in jh.role
        # PM은 요구사항, 스코프 관련 책임을 가져야 함
        responsibilities_str = " ".join(jh.responsibilities)
        assert "요구사항" in responsibilities_str or "스코프" in responsibilities_str

    def test_seul_kim_is_frontend(self, twins):
        """Seul Kim Frontend 역할 테스트"""
        seul = twins["Seul Kim"]
        assert "Frontend" in seul.role
        # Frontend는 UI/UX 관련 책임을 가져야 함
        responsibilities_str = " ".join(seul.responsibilities)
        assert "UI" in responsibilities_str or "UX" in responsibilities_str

    def test_jin_park_is_backend(self, twins):
        """Jin Park Backend 역할 테스트"""
        jin = twins["Jin Park"]
        assert "Backend" in jin.role
        # Backend는 API, DB 관련 책임을 가져야 함
        responsibilities_str = " ".join(jin.responsibilities)
        assert "API" in responsibilities_str or "DB" in responsibilities_str


class TestTwinStyles:
    """트윈 스타일 테스트"""

    @pytest.fixture
    def twins(self):
        return get_twins()

    def test_sam_lee_style_contains_keywords(self, twins):
        """Sam Lee 스타일 키워드 테스트"""
        sam = twins["Sam Lee"]
        # CEO 스타일은 결론, 비용, 리스크 등을 포함해야 함
        style_lower = sam.style.lower()
        assert any(kw in style_lower for kw in ["결론", "비용", "리스크", "고객"])

    def test_jh_kim_style_contains_keywords(self, twins):
        """JH Kim 스타일 키워드 테스트"""
        jh = twins["JH Kim"]
        # PM 스타일은 요구사항, 정리, 기준 등을 포함해야 함
        style_lower = jh.style.lower()
        assert any(kw in style_lower for kw in ["요구사항", "정리", "기준", "acceptance"])

    def test_seul_kim_style_contains_keywords(self, twins):
        """Seul Kim 스타일 키워드 테스트"""
        seul = twins["Seul Kim"]
        # Frontend 스타일은 UX, 사용자, 에러 등을 포함해야 함
        style_lower = seul.style.lower()
        assert any(kw in style_lower for kw in ["ux", "사용자", "에러", "플로우"])

    def test_jin_park_style_contains_keywords(self, twins):
        """Jin Park 스타일 키워드 테스트"""
        jin = twins["Jin Park"]
        # Backend 스타일은 시스템, 성능, 데이터 등을 포함해야 함
        style_lower = jin.style.lower()
        assert any(kw in style_lower for kw in ["시스템", "성능", "데이터", "근거"])
