"""
tests/unit/test_logger.py - Logger 모듈 단위 테스트
TEST-009: Logger 기능 테스트
"""
import pytest
import os

from core.logger import (
    get_logger,
    setup_logger,
    log_request,
    log_response,
    log_llm_call,
    log_error,
    log_security_event,
    log_audit,
    LOG_DIR,
)


class TestGetLogger:
    """get_logger 테스트"""

    def test_get_logger_returns_logger(self):
        """get_logger가 로거를 반환하는지 테스트"""
        logger = get_logger("test_module")
        assert logger is not None

    def test_get_logger_with_name(self):
        """get_logger가 이름이 바인딩된 로거를 반환하는지 테스트"""
        logger = get_logger("custom_name")
        assert logger is not None

    def test_get_logger_default_name(self):
        """get_logger가 기본 이름으로 동작하는지 테스트"""
        logger = get_logger()
        assert logger is not None


class TestSetupLogger:
    """setup_logger 테스트"""

    def test_setup_logger_default(self):
        """기본 설정으로 로거 초기화"""
        # 예외 없이 실행되어야 함
        setup_logger()

    def test_setup_logger_debug_level(self):
        """DEBUG 레벨로 로거 초기화"""
        setup_logger(level="DEBUG")

    def test_setup_logger_no_file(self):
        """파일 로깅 없이 초기화"""
        setup_logger(log_to_file=False)

    def test_setup_logger_no_console(self):
        """콘솔 로깅 없이 초기화"""
        setup_logger(log_to_console=False)

    def test_setup_logger_json_format(self):
        """JSON 포맷으로 초기화"""
        setup_logger(json_logs=True)


class TestLogFunctions:
    """로그 함수 테스트"""

    def test_log_request(self):
        """log_request 함수 테스트"""
        # 예외 없이 실행되어야 함
        log_request("user123", "ask_question", {"question": "테스트"})

    def test_log_request_no_details(self):
        """log_request 상세 정보 없이 테스트"""
        log_request("user123", "ask_question")

    def test_log_response_success(self):
        """log_response 성공 케이스 테스트"""
        log_response("user123", "ask_question", success=True, duration_ms=123.45)

    def test_log_response_failure(self):
        """log_response 실패 케이스 테스트"""
        log_response("user123", "ask_question", success=False, duration_ms=50.0)

    def test_log_llm_call(self):
        """log_llm_call 함수 테스트"""
        log_llm_call(
            provider="claude",
            capability="answerer",
            model="claude-sonnet-4-20250514",
            tokens_in=100,
            tokens_out=200,
            duration_ms=1500.0
        )

    def test_log_llm_call_minimal(self):
        """log_llm_call 최소 인자로 테스트"""
        log_llm_call(provider="mock", capability="router", model="mock")

    def test_log_error(self):
        """log_error 함수 테스트"""
        try:
            raise ValueError("테스트 에러")
        except Exception as e:
            log_error(e, {"context": "테스트"})

    def test_log_error_no_context(self):
        """log_error 컨텍스트 없이 테스트"""
        log_error(Exception("에러 메시지"))

    def test_log_security_event(self):
        """log_security_event 함수 테스트"""
        log_security_event(
            event_type="INJECTION_ATTEMPT",
            details={"input": "suspicious input"},
            severity="HIGH"
        )

    def test_log_security_event_default_severity(self):
        """log_security_event 기본 심각도 테스트"""
        log_security_event(
            event_type="OFFTOPIC",
            details={"message": "off topic content"}
        )

    def test_log_audit(self):
        """log_audit 함수 테스트"""
        log_audit(
            event_type="LOGIN",
            user_id="user123",
            action="authenticate",
            result="success",
            payload={"ip": "127.0.0.1"}
        )

    def test_log_audit_no_payload(self):
        """log_audit 페이로드 없이 테스트"""
        log_audit(
            event_type="LOGOUT",
            user_id="user123",
            action="logout",
            result="success"
        )


class TestLogDirectory:
    """로그 디렉토리 테스트"""

    def test_log_dir_exists(self):
        """로그 디렉토리가 존재하는지 테스트"""
        assert os.path.exists(LOG_DIR)

    def test_log_dir_is_directory(self):
        """로그 경로가 디렉토리인지 테스트"""
        assert os.path.isdir(LOG_DIR)
