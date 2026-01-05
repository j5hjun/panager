"""
토큰 갱신 스케줄러

만료 임박 토큰을 자동으로 갱신합니다.
"""

import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


class TokenRefreshScheduler:
    """
    토큰 갱신 스케줄러

    만료 임박 토큰을 주기적으로 확인하고 갱신합니다.
    """

    def __init__(
        self,
        token_repository: Any,
        oauth_service: Any,
        check_interval_minutes: int = 5,
        refresh_before_minutes: int = 10,
    ):
        """
        TokenRefreshScheduler 초기화

        Args:
            token_repository: TokenRepository 인스턴스
            oauth_service: OAuthService 인스턴스
            check_interval_minutes: 토큰 확인 주기 (분)
            refresh_before_minutes: 만료 몇 분 전에 갱신할지
        """
        self.token_repository = token_repository
        self.oauth_service = oauth_service
        self.check_interval_minutes = check_interval_minutes
        self.refresh_before_minutes = refresh_before_minutes

        # APScheduler 초기화
        self._scheduler = BackgroundScheduler()

        logger.info(
            f"TokenRefreshScheduler 초기화 "
            f"(check_interval={check_interval_minutes}분, "
            f"refresh_before={refresh_before_minutes}분)"
        )

    def start(self) -> None:
        """스케줄러 시작"""
        if self._scheduler.running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            return

        # 주기적 토큰 확인 작업 추가
        self._scheduler.add_job(
            self.check_and_refresh_tokens,
            "interval",
            minutes=self.check_interval_minutes,
            id="token_refresh_job",
            replace_existing=True,
        )

        self._scheduler.start()
        logger.info("토큰 갱신 스케줄러 시작")

    def stop(self) -> None:
        """스케줄러 중지"""
        if not self._scheduler.running:
            logger.warning("스케줄러가 실행 중이 아닙니다")
            return

        self._scheduler.shutdown(wait=False)
        logger.info("토큰 갱신 스케줄러 중지")

    def check_and_refresh_tokens(self) -> None:
        """
        만료 임박 토큰 확인 및 갱신

        refresh_before_minutes 이내에 만료되는 토큰을 찾아서 갱신합니다.
        """
        try:
            # 만료 임박 토큰 조회
            expiring_tokens = self.token_repository.get_expiring_tokens(
                minutes=self.refresh_before_minutes
            )

            if not expiring_tokens:
                logger.debug("만료 임박 토큰 없음")
                return

            logger.info(f"만료 임박 토큰 {len(expiring_tokens)}개 발견")

            # 각 토큰 갱신
            for token in expiring_tokens:
                user_id = token["user_id"]
                provider = token["provider"]

                try:
                    self.oauth_service.refresh_token(user_id, provider)
                    logger.info(f"토큰 갱신 성공: {user_id}/{provider}")
                except Exception as e:
                    logger.error(f"토큰 갱신 실패: {user_id}/{provider} - {e}")
                    # TODO: 사용자에게 알림 전송

        except Exception as e:
            logger.error(f"토큰 갱신 확인 중 오류: {e}")

    def refresh_specific_token(self, user_id: str, provider: str) -> bool:
        """
        특정 토큰 수동 갱신

        Args:
            user_id: 사용자 ID
            provider: 제공자

        Returns:
            갱신 성공 여부
        """
        try:
            self.oauth_service.refresh_token(user_id, provider)
            logger.info(f"토큰 수동 갱신 성공: {user_id}/{provider}")
            return True
        except Exception as e:
            logger.error(f"토큰 수동 갱신 실패: {user_id}/{provider} - {e}")
            return False

    @property
    def is_running(self) -> bool:
        """스케줄러 실행 상태"""
        return self._scheduler.running
