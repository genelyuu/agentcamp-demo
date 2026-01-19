"""
core/errors.py - 에러 핸들링 모듈
ERR-001, ERR-002: Sentry 통합 및 글로벌 예외 핸들러
"""
import os
import functools
from typing import Optional, Callable, Any
from datetime import datetime

from .logger import logger, log_error, log_security_event


# Sentry 설정 (옵션)
_sentry_initialized = False


def init_sentry(dsn: Optional[str] = None) -> bool:
    """
    Sentry 초기화

    Args:
        dsn: Sentry DSN (없으면 환경변수에서 로드)

    Returns:
        초기화 성공 여부
    """
    global _sentry_initialized

    dsn = dsn or os.environ.get("SENTRY_DSN")
    if not dsn:
        logger.warning("Sentry DSN not configured. Error tracking disabled.")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment=os.environ.get("ENVIRONMENT", "development"),
            integrations=[
                LoggingIntegration(
                    level=None,
                    event_level="ERROR"
                )
            ]
        )
        _sentry_initialized = True
        logger.info("Sentry initialized successfully")
        return True

    except ImportError:
        logger.warning("sentry-sdk not installed. Run: pip install sentry-sdk")
        return False
    except Exception as e:
        logger.error(f"Sentry initialization failed: {e}")
        return False


def capture_exception(error: Exception, context: Optional[dict] = None) -> None:
    """
    예외 캡처 (Sentry + 로컬 로깅)

    Args:
        error: 예외 객체
        context: 추가 컨텍스트
    """
    # 로컬 로깅
    log_error(error, context)

    # Sentry 전송 (활성화된 경우)
    if _sentry_initialized:
        try:
            import sentry_sdk
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_extra(key, value)
                sentry_sdk.capture_exception(error)
        except Exception:
            pass  # Sentry 전송 실패는 무시


# 사용자 정의 예외
class AgentCampError(Exception):
    """AgentCamp 기본 예외"""
    def __init__(self, message: str, code: str = "UNKNOWN", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()


class ValidationError(AgentCampError):
    """입력 검증 오류"""
    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        self.field = field


class LLMError(AgentCampError):
    """LLM API 오류"""
    def __init__(self, message: str, provider: str = None, details: dict = None):
        super().__init__(message, code="LLM_ERROR", details=details)
        self.provider = provider


class SecurityError(AgentCampError):
    """보안 관련 오류"""
    def __init__(self, message: str, threat_type: str = None, details: dict = None):
        super().__init__(message, code="SECURITY_ERROR", details=details)
        self.threat_type = threat_type


class StorageError(AgentCampError):
    """저장소 오류"""
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message, code="STORAGE_ERROR", details=details)
        self.operation = operation


# 에러 응답 생성
def create_error_response(error: Exception) -> dict:
    """
    사용자 친화적 에러 응답 생성

    Args:
        error: 예외 객체

    Returns:
        에러 응답 딕셔너리
    """
    if isinstance(error, AgentCampError):
        return {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "timestamp": error.timestamp
            }
        }

    # 일반 예외
    return {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


# 데코레이터
def handle_errors(
    reraise: bool = False,
    default_return: Any = None,
    log_context: Optional[dict] = None
) -> Callable:
    """
    에러 핸들링 데코레이터

    Args:
        reraise: 예외 재발생 여부
        default_return: 에러 시 기본 반환값
        log_context: 로깅 컨텍스트

    Example:
        @handle_errors(default_return="기본값")
        def risky_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AgentCampError as e:
                capture_exception(e, log_context)
                if reraise:
                    raise
                return default_return
            except Exception as e:
                capture_exception(e, log_context)
                if reraise:
                    raise AgentCampError(
                        message=str(e),
                        code="UNEXPECTED_ERROR",
                        details={"original_type": type(e).__name__}
                    )
                return default_return
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    default: Any = None,
    context: Optional[dict] = None,
    **kwargs
) -> Any:
    """
    안전한 함수 실행

    Args:
        func: 실행할 함수
        *args: 위치 인자
        default: 에러 시 기본값
        context: 로깅 컨텍스트
        **kwargs: 키워드 인자

    Returns:
        함수 결과 또는 기본값
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        capture_exception(e, context)
        return default
