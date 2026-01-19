"""
tests/unit/test_errors.py - Errors 모듈 단위 테스트
TEST-010: 에러 핸들링 테스트
"""
import pytest
from datetime import datetime

from core.errors import (
    AgentCampError,
    ValidationError,
    LLMError,
    SecurityError,
    StorageError,
    create_error_response,
    handle_errors,
    safe_execute,
    capture_exception,
)


class TestAgentCampError:
    """AgentCampError 테스트"""

    def test_basic_error(self):
        """기본 에러 생성 테스트"""
        error = AgentCampError("테스트 에러")
        assert str(error) == "테스트 에러"
        assert error.message == "테스트 에러"
        assert error.code == "UNKNOWN"

    def test_error_with_code(self):
        """코드가 있는 에러 테스트"""
        error = AgentCampError("에러", code="CUSTOM_ERROR")
        assert error.code == "CUSTOM_ERROR"

    def test_error_with_details(self):
        """상세 정보가 있는 에러 테스트"""
        error = AgentCampError("에러", details={"key": "value"})
        assert error.details == {"key": "value"}

    def test_error_has_timestamp(self):
        """에러에 타임스탬프가 있는지 테스트"""
        error = AgentCampError("에러")
        assert error.timestamp is not None


class TestValidationError:
    """ValidationError 테스트"""

    def test_validation_error(self):
        """ValidationError 생성 테스트"""
        error = ValidationError("입력 오류", field="email")
        assert error.code == "VALIDATION_ERROR"
        assert error.field == "email"

    def test_validation_error_no_field(self):
        """필드 없이 ValidationError 테스트"""
        error = ValidationError("입력 오류")
        assert error.field is None


class TestLLMError:
    """LLMError 테스트"""

    def test_llm_error(self):
        """LLMError 생성 테스트"""
        error = LLMError("API 오류", provider="claude")
        assert error.code == "LLM_ERROR"
        assert error.provider == "claude"

    def test_llm_error_no_provider(self):
        """프로바이더 없이 LLMError 테스트"""
        error = LLMError("API 오류")
        assert error.provider is None


class TestSecurityError:
    """SecurityError 테스트"""

    def test_security_error(self):
        """SecurityError 생성 테스트"""
        error = SecurityError("보안 위협", threat_type="injection")
        assert error.code == "SECURITY_ERROR"
        assert error.threat_type == "injection"


class TestStorageError:
    """StorageError 테스트"""

    def test_storage_error(self):
        """StorageError 생성 테스트"""
        error = StorageError("저장 실패", operation="write")
        assert error.code == "STORAGE_ERROR"
        assert error.operation == "write"


class TestCreateErrorResponse:
    """create_error_response 테스트"""

    def test_agentcamp_error_response(self):
        """AgentCampError 응답 생성 테스트"""
        error = AgentCampError("테스트 에러", code="TEST_ERROR")
        response = create_error_response(error)

        assert response["success"] is False
        assert response["error"]["code"] == "TEST_ERROR"
        assert response["error"]["message"] == "테스트 에러"

    def test_generic_error_response(self):
        """일반 예외 응답 생성 테스트"""
        error = ValueError("일반 에러")
        response = create_error_response(error)

        assert response["success"] is False
        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert "오류가 발생했습니다" in response["error"]["message"]


class TestHandleErrorsDecorator:
    """handle_errors 데코레이터 테스트"""

    def test_successful_execution(self):
        """성공적인 실행 테스트"""
        @handle_errors()
        def success_func():
            return "success"

        result = success_func()
        assert result == "success"

    def test_error_with_default_return(self):
        """에러 발생 시 기본값 반환 테스트"""
        @handle_errors(default_return="default")
        def error_func():
            raise ValueError("에러")

        result = error_func()
        assert result == "default"

    def test_error_with_reraise(self):
        """에러 재발생 테스트"""
        @handle_errors(reraise=True)
        def error_func():
            raise AgentCampError("에러")

        with pytest.raises(AgentCampError):
            error_func()

    def test_generic_error_wrapped(self):
        """일반 에러가 AgentCampError로 래핑되는지 테스트"""
        @handle_errors(reraise=True)
        def error_func():
            raise ValueError("일반 에러")

        with pytest.raises(AgentCampError):
            error_func()


class TestSafeExecute:
    """safe_execute 테스트"""

    def test_successful_execution(self):
        """성공적인 실행 테스트"""
        def success_func(x, y):
            return x + y

        result = safe_execute(success_func, 1, 2)
        assert result == 3

    def test_error_returns_default(self):
        """에러 발생 시 기본값 반환 테스트"""
        def error_func():
            raise ValueError("에러")

        result = safe_execute(error_func, default="fallback")
        assert result == "fallback"

    def test_error_returns_none_by_default(self):
        """에러 발생 시 기본값 None 테스트"""
        def error_func():
            raise ValueError("에러")

        result = safe_execute(error_func)
        assert result is None

    def test_with_kwargs(self):
        """키워드 인자와 함께 테스트"""
        def func_with_kwargs(a, b=10):
            return a + b

        result = safe_execute(func_with_kwargs, 5, b=20)
        assert result == 25


class TestCaptureException:
    """capture_exception 테스트"""

    def test_capture_with_context(self):
        """컨텍스트와 함께 예외 캡처 테스트"""
        error = ValueError("테스트 에러")
        # 예외 없이 실행되어야 함
        capture_exception(error, {"user_id": "test123"})

    def test_capture_without_context(self):
        """컨텍스트 없이 예외 캡처 테스트"""
        error = ValueError("테스트 에러")
        capture_exception(error)
