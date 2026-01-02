"""
캐시 엔티티

캐시 데이터 모델을 정의합니다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class CachedData:
    """
    캐시된 데이터 모델

    Attributes:
        key: 캐시 키
        value: 캐시 값 (JSON 직렬화 가능한 데이터)
        created_at: 생성 시간
        expires_at: 만료 시간
    """

    key: str
    value: Any
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        """캐시가 만료되었는지 확인"""
        return datetime.now() >= self.expires_at

    def ttl_seconds(self) -> int:
        """남은 TTL(초) 반환, 만료 시 0"""
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, int(remaining))


def generate_cache_key(prefix: str, **kwargs: Any) -> str:
    """
    캐시 키 생성

    Args:
        prefix: 키 접두사 (예: "weather", "directions")
        **kwargs: 키에 포함할 파라미터

    Returns:
        생성된 캐시 키 (예: "weather:city=seoul")
    """
    if not kwargs:
        return prefix

    params = [f"{k}={v}" for k, v in sorted(kwargs.items())]
    return f"{prefix}:{','.join(params)}"
