"""
core/llm/error_handler.py - LLM 오류 처리 유틸리티
SEC-001, SEC-002: API 오류 메시지 일반화
"""
from typing import Optional, Dict, Any

from core.logger import get_logger

logger = get_logger("llm_error")


# 사용자에게 보여줄 일반 메시지 매핑
USER_FRIENDLY_MESSAGES: Dict[str, str] = {
    # Anthropic 예외
    "AuthenticationError": "API 인증에 실패했습니다. 관리자에게 문의하세요.",
    "PermissionDeniedError": "API 접근 권한이 없습니다. 관리자에게 문의하세요.",
    "RateLimitError": "요청이 너무 많습니다. 잠시 후 다시 시도하세요.",
    "APIConnectionError": "서버 연결에 실패했습니다. 네트워크를 확인하세요.",
    "APIStatusError": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도하세요.",
    "BadRequestError": "잘못된 요청입니다. 입력을 확인하세요.",

    # OpenAI 예외
    "OpenAIError": "AI 서비스 오류가 발생했습니다. 잠시 후 다시 시도하세요.",
    "APIError": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도하세요.",
    "Timeout": "요청 시간이 초과되었습니다. 다시 시도하세요.",
    "APITimeoutError": "요청 시간이 초과되었습니다. 다시 시도하세요.",

    # 일반 예외
    "ConnectionError": "서버 연결에 실패했습니다. 네트워크를 확인하세요.",
    "TimeoutError": "요청 시간이 초과되었습니다. 다시 시도하세요.",
    "ValueError": "잘못된 입력입니다. 입력을 확인하세요.",
    "ImportError": "필요한 패키지가 설치되지 않았습니다. 관리자에게 문의하세요.",

    # 기본값
    "default": "일시적인 오류가 발생했습니다. 다시 시도해주세요."
}


def sanitize_error(e: Exception) -> str:
    """
    예외를 사용자 친화적 메시지로 변환

    Args:
        e: 예외 객체

    Returns:
        사용자 친화적 오류 메시지
    """
    error_type = type(e).__name__
    return USER_FRIENDLY_MESSAGES.get(error_type, USER_FRIENDLY_MESSAGES["default"])


def log_llm_error(
    e: Exception,
    provider: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    LLM 오류를 상세히 로깅 (내부용)

    Args:
        e: 예외 객체
        provider: LLM 프로바이더 이름 ("claude", "openai")
        context: 추가 컨텍스트 정보
    """
    error_type = type(e).__name__
    error_message = str(e)

    # 민감 정보 마스킹 (API 키 패턴)
    masked_message = _mask_sensitive_info(error_message)

    logger.error(
        f"LLM_ERROR | provider={provider} | type={error_type} | "
        f"message={masked_message} | context={context or {}}"
    )


def _mask_sensitive_info(message: str) -> str:
    """
    민감 정보 마스킹

    Args:
        message: 원본 메시지

    Returns:
        마스킹된 메시지
    """
    import re

    # API 키 패턴 마스킹
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', 'sk-***MASKED***'),  # OpenAI
        (r'sk-ant-[a-zA-Z0-9]{20,}', 'sk-ant-***MASKED***'),  # Anthropic
        (r'api[_-]?key["\s:=]+["\']?[a-zA-Z0-9-]+["\']?', 'api_key=***MASKED***'),
    ]

    result = message
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def format_error_response(e: Exception, provider: str) -> str:
    """
    오류 응답 포맷팅 (로깅 + 사용자 메시지 반환)

    Args:
        e: 예외 객체
        provider: LLM 프로바이더 이름

    Returns:
        사용자 친화적 오류 메시지
    """
    log_llm_error(e, provider)
    return f"[{provider.upper()} 오류] {sanitize_error(e)}"
