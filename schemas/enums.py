"""
schemas/enums.py - Enum 정의
SCHEMA-006: KnowledgeTag Enum
SCHEMA-007: KnowledgeSource Enum
"""
from enum import Enum


class KnowledgeTag(str, Enum):
    """지식 항목 태그 (SCHEMA-006)"""
    RULE = "rule"           # 규칙/원칙
    PITFALL = "pitfall"     # 함정/실수
    GLOSSARY = "glossary"   # 용어 정의
    PROCESS = "process"     # 프로세스/절차


class KnowledgeSource(str, Enum):
    """지식 소스 타입 (SCHEMA-007)"""
    MEETING_STT = "meeting_stt"       # 회의 STT
    SLACK_DISCORD = "slack_discord"   # Slack/Discord 대화
    CLIENT_STT = "client_stt"         # 고객 미팅 STT


class RiskCategory(str, Enum):
    """리스크 카테고리 (RISK-001)"""
    HALLUCINATION = "halluc"    # 사실과 다른 정보 생성
    BIAS = "bias"               # 편향된 응답
    PII_LEAK = "pii_leak"       # 개인정보 노출
    INJECTION = "injection"     # 프롬프트 인젝션
    MISROUTE = "misroute"       # 잘못된 멘토 라우팅
    OFFTOPIC = "offtopic"       # 주제 이탈


class Severity(str, Enum):
    """심각도 레벨 (RISK-002)"""
    CRITICAL = "critical"   # 즉시 대응
    HIGH = "high"           # 24시간 내 대응
    MEDIUM = "medium"       # 1주 내 대응
    LOW = "low"             # 백로그


class IncidentStatus(str, Enum):
    """인시던트 상태"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    MITIGATED = "mitigated"
    CLOSED = "closed"
