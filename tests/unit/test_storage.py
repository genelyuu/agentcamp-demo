"""
tests/unit/test_storage.py - Storage 모듈 단위 테스트
TEST-002: Storage CRUD 테스트
"""
import json
import os
import tempfile
import pytest
from unittest.mock import patch

from core.storage import (
    load_json,
    save_json,
    get_org,
    set_org,
    get_knowledge,
    set_knowledge,
    get_sessions,
    set_sessions,
    get_org_config,
    set_org_config,
    get_knowledge_base,
    set_knowledge_base,
    get_session_store,
    set_session_store,
)
from schemas import OrgConfig, KnowledgeBase, SessionStore


class TestStorageBasic:
    """기본 JSON 저장/로드 테스트"""

    def test_load_json_returns_dict(self):
        """load_json이 딕셔너리를 반환하는지 테스트"""
        result = get_org()
        assert isinstance(result, dict)

    def test_org_has_required_fields(self):
        """org.json에 필수 필드가 있는지 테스트"""
        org = get_org()
        assert "company" in org
        assert "role" in org

    def test_knowledge_has_items(self):
        """knowledge.json에 items 필드가 있는지 테스트"""
        knowledge = get_knowledge()
        assert "items" in knowledge
        assert isinstance(knowledge["items"], list)

    def test_sessions_has_users(self):
        """sessions.json에 users 필드가 있는지 테스트"""
        sessions = get_sessions()
        assert "users" in sessions
        assert isinstance(sessions["users"], dict)


class TestStorageCRUD:
    """CRUD 연산 테스트"""

    def test_set_and_get_org(self):
        """org 설정/조회 테스트"""
        original = get_org()

        # 수정
        modified = original.copy()
        modified["test_field"] = "test_value"
        set_org(modified)

        # 확인
        result = get_org()
        assert result["test_field"] == "test_value"

        # 복원
        del modified["test_field"]
        set_org(modified)

    def test_set_and_get_knowledge(self):
        """knowledge 설정/조회 테스트"""
        original = get_knowledge()

        # 수정
        modified = original.copy()
        modified["test_item"] = "test"
        set_knowledge(modified)

        # 확인
        result = get_knowledge()
        assert result["test_item"] == "test"

        # 복원
        del modified["test_item"]
        set_knowledge(modified)

    def test_set_and_get_sessions(self):
        """sessions 설정/조회 테스트"""
        original = get_sessions()

        # 수정
        modified = original.copy()
        modified["users"]["test_user"] = {"name": "Test"}
        set_sessions(modified)

        # 확인
        result = get_sessions()
        assert "test_user" in result["users"]

        # 복원
        del modified["users"]["test_user"]
        set_sessions(modified)


class TestPydanticHelpers:
    """Pydantic 모델 헬퍼 함수 테스트"""

    def test_get_org_config_returns_model(self):
        """get_org_config가 OrgConfig 모델을 반환하는지 테스트"""
        config = get_org_config()
        assert isinstance(config, OrgConfig)
        assert hasattr(config, "company")
        assert hasattr(config, "role")

    def test_set_org_config_saves_model(self):
        """set_org_config가 모델을 저장하는지 테스트"""
        original = get_org_config()

        # 수정 및 저장
        modified = OrgConfig(
            company=original.company,
            role=original.role,
            tools=original.tools,
            rubric=original.rubric
        )
        set_org_config(modified)

        # 확인
        result = get_org_config()
        assert result.company == modified.company

    def test_get_knowledge_base_returns_model(self):
        """get_knowledge_base가 KnowledgeBase 모델을 반환하는지 테스트"""
        kb = get_knowledge_base()
        assert isinstance(kb, KnowledgeBase)
        assert hasattr(kb, "items")

    def test_get_session_store_returns_model(self):
        """get_session_store가 SessionStore 모델을 반환하는지 테스트"""
        store = get_session_store()
        assert isinstance(store, SessionStore)
        assert hasattr(store, "users")
