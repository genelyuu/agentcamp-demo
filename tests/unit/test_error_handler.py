"""
tests/unit/test_error_handler.py - LLM Error Handler 단위 테스트
TEST-012: Error Handler 기능 테스트
"""
import pytest

from core.llm.error_handler import (
    sanitize_error,
    log_llm_error,
    format_error_response,
    _mask_sensitive_info,
    USER_FRIENDLY_MESSAGES,
)


class TestSanitizeError:
    """sanitize_error 테스트"""

    def test_authentication_error(self):
        """AuthenticationError 메시지 테스트"""
        class AuthenticationError(Exception):
            pass

        error = AuthenticationError("Invalid API key")
        result = sanitize_error(error)
        assert "인증" in result

    def test_rate_limit_error(self):
        """RateLimitError 메시지 테스트"""
        class RateLimitError(Exception):
            pass

        error = RateLimitError("Rate limit exceeded")
        result = sanitize_error(error)
        assert "요청이 너무 많습니다" in result

    def test_connection_error(self):
        """ConnectionError 메시지 테스트"""
        error = ConnectionError("Connection refused")
        result = sanitize_error(error)
        assert "연결" in result

    def test_timeout_error(self):
        """TimeoutError 메시지 테스트"""
        error = TimeoutError("Request timed out")
        result = sanitize_error(error)
        assert "시간" in result

    def test_value_error(self):
        """ValueError 메시지 테스트"""
        error = ValueError("Invalid value")
        result = sanitize_error(error)
        assert "입력" in result

    def test_unknown_error(self):
        """알 수 없는 에러 메시지 테스트"""
        class CustomError(Exception):
            pass

        error = CustomError("Unknown error")
        result = sanitize_error(error)
        assert result == USER_FRIENDLY_MESSAGES["default"]


class TestMaskSensitiveInfo:
    """_mask_sensitive_info 테스트"""

    def test_mask_openai_key(self):
        """OpenAI API 키 마스킹 테스트"""
        message = "Error with key sk-abc123def456ghijklmnopqrstuvwxyz"
        result = _mask_sensitive_info(message)
        assert "sk-abc123" not in result
        assert "MASKED" in result

    def test_mask_anthropic_key(self):
        """Anthropic API 키 마스킹 테스트"""
        message = "Error with key sk-ant-abc123def456ghijklmnopqrstuvwxyz"
        result = _mask_sensitive_info(message)
        assert "sk-ant-abc123" not in result
        assert "MASKED" in result

    def test_mask_api_key_pattern(self):
        """api_key 패턴 마스킹 테스트"""
        message = 'api_key="secret123456"'
        result = _mask_sensitive_info(message)
        assert "secret123456" not in result
        assert "MASKED" in result

    def test_no_sensitive_info(self):
        """민감 정보 없는 메시지 테스트"""
        message = "Normal error message without secrets"
        result = _mask_sensitive_info(message)
        assert result == message


class TestLogLLMError:
    """log_llm_error 테스트"""

    def test_log_error_claude(self):
        """Claude 에러 로깅 테스트"""
        error = ValueError("Test error")
        # 예외 없이 실행되어야 함
        log_llm_error(error, "claude", {"model": "claude-3"})

    def test_log_error_openai(self):
        """OpenAI 에러 로깅 테스트"""
        error = ConnectionError("Connection failed")
        log_llm_error(error, "openai", {"model": "gpt-4"})

    def test_log_error_no_context(self):
        """컨텍스트 없이 에러 로깅 테스트"""
        error = Exception("Generic error")
        log_llm_error(error, "mock")


class TestFormatErrorResponse:
    """format_error_response 테스트"""

    def test_format_claude_error(self):
        """Claude 에러 포맷 테스트"""
        error = ValueError("Invalid input")
        result = format_error_response(error, "claude")

        assert "[CLAUDE 오류]" in result
        assert "입력" in result

    def test_format_openai_error(self):
        """OpenAI 에러 포맷 테스트"""
        error = TimeoutError("Timeout")
        result = format_error_response(error, "openai")

        assert "[OPENAI 오류]" in result
        assert "시간" in result

    def test_format_unknown_provider(self):
        """알 수 없는 프로바이더 에러 포맷 테스트"""
        error = Exception("Error")
        result = format_error_response(error, "unknown")

        assert "[UNKNOWN 오류]" in result


class TestUserFriendlyMessages:
    """USER_FRIENDLY_MESSAGES 상수 테스트"""

    def test_has_default_message(self):
        """기본 메시지 존재 테스트"""
        assert "default" in USER_FRIENDLY_MESSAGES

    def test_has_common_error_types(self):
        """일반적인 에러 타입 메시지 존재 테스트"""
        expected_types = [
            "AuthenticationError",
            "RateLimitError",
            "APIConnectionError",
            "ConnectionError",
            "TimeoutError",
        ]
        for error_type in expected_types:
            assert error_type in USER_FRIENDLY_MESSAGES

    def test_messages_are_korean(self):
        """메시지가 한국어인지 테스트"""
        for key, message in USER_FRIENDLY_MESSAGES.items():
            # 한글이 포함되어 있는지 확인
            has_korean = any('\uac00' <= char <= '\ud7a3' for char in message)
            assert has_korean, f"{key} 메시지에 한국어가 없습니다: {message}"
