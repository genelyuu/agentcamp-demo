"""
tests/unit/test_schemas.py - Pydantic 스키마 단위 테스트
TEST-013: 모든 스키마 모듈 테스트
"""
import pytest
from datetime import datetime

from schemas import (
    # Enums
    KnowledgeTag,
    KnowledgeSource,
    RiskCategory,
    Severity,
    IncidentStatus,
    # Knowledge
    KnowledgeItem,
    KnowledgeBase,
    # Organization
    OrgConfig,
    RubricConfig,
    # Session
    UserSession,
    SessionStore,
    OJTTask,
    ChatMessage,
    # Audit
    AuditEvent,
    # Risk
    RiskEntry,
    Incident,
    RiskRegister,
    IncidentLog,
)


class TestEnums:
    """Enum 테스트"""

    def test_knowledge_tag_values(self):
        """KnowledgeTag enum 값 테스트"""
        assert KnowledgeTag.RULE.value == "rule"
        assert KnowledgeTag.PITFALL.value == "pitfall"
        assert KnowledgeTag.GLOSSARY.value == "glossary"
        assert KnowledgeTag.PROCESS.value == "process"

    def test_knowledge_source_values(self):
        """KnowledgeSource enum 값 테스트"""
        assert KnowledgeSource.MEETING_STT.value == "meeting_stt"
        assert KnowledgeSource.SLACK_DISCORD.value == "slack_discord"
        assert KnowledgeSource.CLIENT_STT.value == "client_stt"

    def test_risk_category_values(self):
        """RiskCategory enum 값 테스트"""
        assert RiskCategory.HALLUCINATION.value == "halluc"
        assert RiskCategory.BIAS.value == "bias"
        assert RiskCategory.PII_LEAK.value == "pii_leak"
        assert RiskCategory.INJECTION.value == "injection"
        assert RiskCategory.MISROUTE.value == "misroute"
        assert RiskCategory.OFFTOPIC.value == "offtopic"

    def test_severity_values(self):
        """Severity enum 값 테스트"""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_incident_status_values(self):
        """IncidentStatus enum 값 테스트"""
        assert IncidentStatus.OPEN.value == "open"
        assert IncidentStatus.INVESTIGATING.value == "investigating"
        assert IncidentStatus.RESOLVED.value == "resolved"
        assert IncidentStatus.MITIGATED.value == "mitigated"
        assert IncidentStatus.CLOSED.value == "closed"


class TestKnowledgeItem:
    """KnowledgeItem 테스트"""

    def test_create_knowledge_item(self):
        """KnowledgeItem 생성 테스트"""
        item = KnowledgeItem(
            id="K-001",
            text="테스트 지식 내용",
            tag=KnowledgeTag.RULE,
            source=KnowledgeSource.MEETING_STT
        )
        assert item.id == "K-001"
        assert item.text == "테스트 지식 내용"
        assert item.tag == "rule"
        assert item.source == "meeting_stt"

    def test_knowledge_item_has_timestamp(self):
        """KnowledgeItem 타임스탬프 테스트"""
        item = KnowledgeItem(
            id="K-002",
            text="타임스탬프 테스트",
            tag=KnowledgeTag.PITFALL,
            source=KnowledgeSource.SLACK_DISCORD
        )
        assert item.created_at is not None
        assert isinstance(item.created_at, datetime)

    def test_knowledge_item_text_min_length(self):
        """KnowledgeItem 텍스트 최소 길이 테스트"""
        with pytest.raises(ValueError):
            KnowledgeItem(
                id="K-003",
                text="",  # min_length=1 위반
                tag=KnowledgeTag.RULE,
                source=KnowledgeSource.MEETING_STT
            )

    def test_knowledge_item_text_max_length(self):
        """KnowledgeItem 텍스트 최대 길이 테스트"""
        with pytest.raises(ValueError):
            KnowledgeItem(
                id="K-004",
                text="a" * 1001,  # max_length=1000 위반
                tag=KnowledgeTag.RULE,
                source=KnowledgeSource.MEETING_STT
            )


class TestKnowledgeBase:
    """KnowledgeBase 테스트"""

    def test_create_empty_knowledge_base(self):
        """빈 KnowledgeBase 생성 테스트"""
        kb = KnowledgeBase()
        assert kb.items == []

    def test_knowledge_base_with_items(self):
        """아이템이 있는 KnowledgeBase 테스트"""
        item = KnowledgeItem(
            id="K-001",
            text="지식 내용",
            tag=KnowledgeTag.RULE,
            source=KnowledgeSource.MEETING_STT
        )
        kb = KnowledgeBase(items=[item])
        assert len(kb.items) == 1
        assert kb.items[0].id == "K-001"


class TestRubricConfig:
    """RubricConfig 테스트"""

    def test_default_rubric_config(self):
        """기본 RubricConfig 테스트"""
        rubric = RubricConfig()
        assert "원인" in rubric.acceptance_keywords
        assert "재현" in rubric.acceptance_keywords
        assert "재발방지" in rubric.acceptance_keywords
        assert "로그" in rubric.acceptance_keywords

    def test_custom_rubric_config(self):
        """커스텀 RubricConfig 테스트"""
        rubric = RubricConfig(acceptance_keywords=["테스트", "검증"])
        assert rubric.acceptance_keywords == ["테스트", "검증"]


class TestOrgConfig:
    """OrgConfig 테스트"""

    def test_create_org_config(self):
        """OrgConfig 생성 테스트"""
        org = OrgConfig(company="테스트회사")
        assert org.company == "테스트회사"
        assert org.role == "Backend Engineer"
        assert "Slack" in org.tools
        assert "GitHub" in org.tools

    def test_org_config_with_custom_values(self):
        """커스텀 값으로 OrgConfig 생성 테스트"""
        org = OrgConfig(
            company="커스텀회사",
            role="Frontend Engineer",
            tools=["Jira", "Confluence"]
        )
        assert org.company == "커스텀회사"
        assert org.role == "Frontend Engineer"
        assert org.tools == ["Jira", "Confluence"]

    def test_org_config_company_min_length(self):
        """OrgConfig 회사명 최소 길이 테스트"""
        with pytest.raises(ValueError):
            OrgConfig(company="")

    def test_org_config_company_max_length(self):
        """OrgConfig 회사명 최대 길이 테스트"""
        with pytest.raises(ValueError):
            OrgConfig(company="a" * 101)

    def test_org_config_has_rubric(self):
        """OrgConfig에 rubric 필드 테스트"""
        org = OrgConfig(company="테스트회사")
        assert org.rubric is not None
        assert isinstance(org.rubric, RubricConfig)


class TestChatMessage:
    """ChatMessage 테스트"""

    def test_create_chat_message(self):
        """ChatMessage 생성 테스트"""
        msg = ChatMessage(role="user", content="안녕하세요")
        assert msg.role == "user"
        assert msg.content == "안녕하세요"
        assert msg.twin_name is None
        assert msg.timestamp is None

    def test_chat_message_with_twin(self):
        """Twin 정보가 있는 ChatMessage 테스트"""
        msg = ChatMessage(
            role="assistant",
            content="답변입니다",
            twin_name="Jin Park",
            timestamp="2026-01-19T10:00:00"
        )
        assert msg.twin_name == "Jin Park"
        assert msg.timestamp == "2026-01-19T10:00:00"


class TestOJTTask:
    """OJTTask 테스트"""

    def test_create_ojt_task(self):
        """OJTTask 생성 테스트"""
        task = OJTTask(
            title="버그 수정",
            context="로그인 오류가 발생합니다",
            deliverable="수정된 코드와 테스트"
        )
        assert task.title == "버그 수정"
        assert task.context == "로그인 오류가 발생합니다"
        assert task.deliverable == "수정된 코드와 테스트"
        assert task.acceptance_keywords == []

    def test_ojt_task_with_keywords(self):
        """키워드가 있는 OJTTask 테스트"""
        task = OJTTask(
            title="성능 개선",
            context="API 응답 속도가 느립니다",
            deliverable="최적화된 쿼리",
            acceptance_keywords=["인덱스", "캐시", "쿼리"]
        )
        assert len(task.acceptance_keywords) == 3


class TestUserSession:
    """UserSession 테스트"""

    def test_create_user_session(self):
        """UserSession 생성 테스트"""
        session = UserSession(user_id="user001", name="테스트 유저")
        assert session.user_id == "user001"
        assert session.name == "테스트 유저"
        assert session.adapt_score == 50.0
        assert session.risk_score == 50.0
        assert session.tasks_done == 0
        assert session.questions == 0

    def test_user_session_score_clamping(self):
        """점수 클램핑 테스트"""
        # 범위 초과 값은 클램핑되어야 함
        session = UserSession(
            user_id="user002",
            name="테스트",
            adapt_score=150.0,  # 100 초과
            risk_score=-10.0   # 0 미만
        )
        assert session.adapt_score == 100.0
        assert session.risk_score == 0.0

    def test_user_session_with_task(self):
        """미션이 있는 UserSession 테스트"""
        task = OJTTask(
            title="테스트 미션",
            context="상황 설명",
            deliverable="제출물"
        )
        session = UserSession(
            user_id="user003",
            name="테스트",
            last_task=task
        )
        assert session.last_task is not None
        assert session.last_task.title == "테스트 미션"

    def test_user_session_user_id_length(self):
        """user_id 길이 테스트"""
        with pytest.raises(ValueError):
            UserSession(user_id="", name="테스트")

        with pytest.raises(ValueError):
            UserSession(user_id="a" * 51, name="테스트")


class TestSessionStore:
    """SessionStore 테스트"""

    def test_create_empty_session_store(self):
        """빈 SessionStore 생성 테스트"""
        store = SessionStore()
        assert store.users == {}

    def test_session_store_with_users(self):
        """유저가 있는 SessionStore 테스트"""
        user = UserSession(user_id="user001", name="테스트")
        store = SessionStore(users={"user001": user})
        assert "user001" in store.users
        assert store.users["user001"].name == "테스트"


class TestAuditEvent:
    """AuditEvent 테스트"""

    def test_create_audit_event(self):
        """AuditEvent 생성 테스트"""
        event = AuditEvent(
            event_type="question",
            result="success"
        )
        assert event.event_type == "question"
        assert event.result == "success"
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.trace_id is not None

    def test_audit_event_with_user_and_payload(self):
        """유저와 페이로드가 있는 AuditEvent 테스트"""
        event = AuditEvent(
            event_type="submission",
            user_id="user001",
            payload={"task_id": "T-001", "score": 85},
            result="success"
        )
        assert event.user_id == "user001"
        assert event.payload["task_id"] == "T-001"
        assert event.payload["score"] == 85


class TestRiskEntry:
    """RiskEntry 테스트"""

    def test_create_risk_entry(self):
        """RiskEntry 생성 테스트"""
        risk = RiskEntry(
            category=RiskCategory.HALLUCINATION,
            description="모델이 거짓 정보를 생성할 수 있음",
            likelihood=3,
            impact=4,
            owner="AI팀"
        )
        assert risk.category == "halluc"
        assert risk.description == "모델이 거짓 정보를 생성할 수 있음"
        assert risk.likelihood == 3
        assert risk.impact == 4
        assert risk.owner == "AI팀"
        assert risk.risk_id.startswith("R-")

    def test_risk_score_computed(self):
        """리스크 점수 계산 테스트"""
        risk = RiskEntry(
            category=RiskCategory.INJECTION,
            description="프롬프트 인젝션 위험",
            likelihood=4,
            impact=5,
            owner="보안팀"
        )
        assert risk.risk_score == 20  # 4 * 5

    def test_risk_level_critical(self):
        """Critical 리스크 레벨 테스트"""
        risk = RiskEntry(
            category=RiskCategory.PII_LEAK,
            description="개인정보 노출",
            likelihood=5,
            impact=5,
            owner="보안팀"
        )
        assert risk.risk_level == "critical"

    def test_risk_level_high(self):
        """High 리스크 레벨 테스트"""
        risk = RiskEntry(
            category=RiskCategory.BIAS,
            description="편향된 응답",
            likelihood=3,
            impact=4,
            owner="AI팀"
        )
        assert risk.risk_level == "high"

    def test_risk_level_medium(self):
        """Medium 리스크 레벨 테스트"""
        risk = RiskEntry(
            category=RiskCategory.MISROUTE,
            description="잘못된 라우팅",
            likelihood=2,
            impact=3,
            owner="개발팀"
        )
        assert risk.risk_level == "medium"

    def test_risk_level_low(self):
        """Low 리스크 레벨 테스트"""
        risk = RiskEntry(
            category=RiskCategory.OFFTOPIC,
            description="주제 이탈",
            likelihood=1,
            impact=2,
            owner="운영팀"
        )
        assert risk.risk_level == "low"

    def test_risk_entry_likelihood_range(self):
        """likelihood 범위 검증 테스트"""
        with pytest.raises(ValueError):
            RiskEntry(
                category=RiskCategory.HALLUCINATION,
                description="테스트",
                likelihood=0,  # ge=1 위반
                impact=3,
                owner="테스트"
            )

        with pytest.raises(ValueError):
            RiskEntry(
                category=RiskCategory.HALLUCINATION,
                description="테스트",
                likelihood=6,  # le=5 위반
                impact=3,
                owner="테스트"
            )

    def test_risk_entry_impact_range(self):
        """impact 범위 검증 테스트"""
        with pytest.raises(ValueError):
            RiskEntry(
                category=RiskCategory.HALLUCINATION,
                description="테스트",
                likelihood=3,
                impact=0,  # ge=1 위반
                owner="테스트"
            )


class TestIncident:
    """Incident 테스트"""

    def test_create_incident(self):
        """Incident 생성 테스트"""
        incident = Incident(
            category=RiskCategory.INJECTION,
            severity=Severity.HIGH,
            description="프롬프트 인젝션 시도 감지",
            trigger="악의적인 사용자 입력"
        )
        assert incident.category == "injection"
        assert incident.severity == "high"
        assert incident.description == "프롬프트 인젝션 시도 감지"
        assert incident.trigger == "악의적인 사용자 입력"
        assert incident.incident_id.startswith("INC-")
        assert incident.status == "open"

    def test_incident_with_mitigation(self):
        """완화 조치가 있는 Incident 테스트"""
        incident = Incident(
            category=RiskCategory.PII_LEAK,
            severity=Severity.CRITICAL,
            description="개인정보 노출 사고",
            trigger="필터 우회",
            mitigation="즉시 차단 및 로그 삭제",
            rca="입력 검증 미흡"
        )
        assert incident.mitigation == "즉시 차단 및 로그 삭제"
        assert incident.rca == "입력 검증 미흡"


class TestRiskRegister:
    """RiskRegister 테스트"""

    def test_create_empty_risk_register(self):
        """빈 RiskRegister 생성 테스트"""
        register = RiskRegister()
        assert register.risks == []

    def test_risk_register_with_risks(self):
        """리스크가 있는 RiskRegister 테스트"""
        risk = RiskEntry(
            category=RiskCategory.HALLUCINATION,
            description="테스트 리스크",
            likelihood=2,
            impact=3,
            owner="테스트"
        )
        register = RiskRegister(risks=[risk])
        assert len(register.risks) == 1


class TestIncidentLog:
    """IncidentLog 테스트"""

    def test_create_empty_incident_log(self):
        """빈 IncidentLog 생성 테스트"""
        log = IncidentLog()
        assert log.incidents == []

    def test_incident_log_with_incidents(self):
        """인시던트가 있는 IncidentLog 테스트"""
        incident = Incident(
            category=RiskCategory.BIAS,
            severity=Severity.MEDIUM,
            description="편향된 응답 감지",
            trigger="모델 응답"
        )
        log = IncidentLog(incidents=[incident])
        assert len(log.incidents) == 1
