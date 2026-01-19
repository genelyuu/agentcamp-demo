"""
core/logger.py - 로깅 설정 모듈
LOG-002: loguru 기반 로깅 설정
"""
import sys
import os
from datetime import datetime
from typing import Optional

from loguru import logger

# 로그 디렉토리
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 기본 로그 포맷
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# JSON 로그 포맷 (파일용)
JSON_FORMAT = (
    '{{"timestamp":"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}",'
    '"level":"{level}",'
    '"module":"{name}",'
    '"function":"{function}",'
    '"line":{line},'
    '"message":"{message}"}}'
)


def setup_logger(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_logs: bool = False
) -> None:
    """
    로거 설정

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: 파일 로깅 여부
        log_to_console: 콘솔 로깅 여부
        json_logs: JSON 포맷 사용 여부
    """
    # 기존 핸들러 제거
    logger.remove()

    # 콘솔 로깅
    if log_to_console:
        logger.add(
            sys.stderr,
            format=LOG_FORMAT,
            level=level,
            colorize=True
        )

    # 파일 로깅
    if log_to_file:
        log_file = os.path.join(LOG_DIR, "agentcamp_{time:YYYY-MM-DD}.log")
        file_format = JSON_FORMAT if json_logs else LOG_FORMAT

        logger.add(
            log_file,
            format=file_format,
            level=level,
            rotation="00:00",  # 자정에 로테이션
            retention="7 days",  # 7일 보관
            compression="gz",  # 압축
            encoding="utf-8"
        )

    logger.info(f"Logger initialized: level={level}, file={log_to_file}, console={log_to_console}")


def get_logger(name: str = "agentcamp"):
    """
    모듈별 로거 반환

    Args:
        name: 모듈 이름

    Returns:
        loguru logger 인스턴스
    """
    return logger.bind(name=name)


# 편의 함수들
def log_request(user_id: str, action: str, details: Optional[dict] = None) -> None:
    """사용자 요청 로깅"""
    logger.info(
        f"REQUEST | user={user_id} | action={action} | details={details or {}}"
    )


def log_response(user_id: str, action: str, success: bool, duration_ms: float) -> None:
    """응답 로깅"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(
        f"RESPONSE | user={user_id} | action={action} | status={status} | duration={duration_ms:.2f}ms"
    )


def log_llm_call(
    provider: str,
    capability: str,
    model: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    duration_ms: float = 0
) -> None:
    """LLM API 호출 로깅"""
    logger.info(
        f"LLM_CALL | provider={provider} | capability={capability} | model={model} | "
        f"tokens_in={tokens_in} | tokens_out={tokens_out} | duration={duration_ms:.2f}ms"
    )


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """에러 로깅"""
    logger.error(
        f"ERROR | type={type(error).__name__} | message={str(error)} | context={context or {}}"
    )


def log_security_event(event_type: str, details: dict, severity: str = "MEDIUM") -> None:
    """보안 이벤트 로깅"""
    logger.warning(
        f"SECURITY | type={event_type} | severity={severity} | details={details}"
    )


def log_audit(
    event_type: str,
    user_id: str,
    action: str,
    result: str,
    payload: Optional[dict] = None
) -> None:
    """감사 로그"""
    logger.info(
        f"AUDIT | event={event_type} | user={user_id} | action={action} | "
        f"result={result} | payload={payload or {}}"
    )


# 초기화 (기본 설정)
# 실제 앱에서는 setup_logger()를 명시적으로 호출
_initialized = False

def ensure_initialized():
    """로거 초기화 확인"""
    global _initialized
    if not _initialized:
        setup_logger(level="INFO", log_to_file=True, log_to_console=True)
        _initialized = True


# 모듈 로드 시 기본 초기화
ensure_initialized()
