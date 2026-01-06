"""
통합형 능동적 AI 비서 "패니저" - 메인 진입점

이 모듈은 애플리케이션의 시작점입니다.
v2.0: 자율 판단 시스템 + 메모리 시스템 (P-010, P-011)
v2.1: 다중 사용자 시스템 (P-014)
"""

import asyncio
import logging
import os
import sys
import threading

from src.adapters.oauth.server import create_oauth_app
from src.adapters.slack.handler import SlackHandler
from src.adapters.slack.oauth_commands import SlackOAuthCommands
from src.config.settings import get_settings

# P-014: OAuth 모듈
from src.core.auth.oauth_service import OAuthService
from src.core.auth.token_repository import TokenRepository
from src.core.auth.token_scheduler import TokenRefreshScheduler
from src.core.autonomous.memory.memory_manager import MemoryManager
from src.services.llm.ai_service import AIService
from src.services.scheduler.scheduler import SchedulerService


def setup_logging() -> None:
    """로깅 설정"""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def create_message_callback(ai_service: AIService):
    """Slack 메시지 콜백 생성"""

    def callback(event: dict) -> str:
        """동기 콜백 (Slack bolt는 동기 함수 필요)"""
        user_id = event.get("user", "unknown")
        text = event.get("text", "")
        msg_type = event.get("type", "dm")

        logger = logging.getLogger(__name__)
        logger.info(f"메시지 처리 중: {user_id} ({msg_type}): {text[:50]}...")

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response = loop.run_until_complete(ai_service.chat(user_id, text))
        return response

    return callback


def start_oauth_server(oauth_service: OAuthService, port: int = 8080) -> None:
    """OAuth 콜백 서버 시작 (백그라운드 스레드)"""
    import uvicorn

    app = create_oauth_app(oauth_service)

    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()


def main() -> None:
    """애플리케이션 메인 함수"""
    setup_logging()
    logger = logging.getLogger(__name__)

    settings = get_settings()
    logger.info(f"🤵 {settings.assistant_name} AI 비서를 시작합니다...")
    logger.info(f"📡 LLM Provider: {settings.llm_provider}")
    logger.info(f"🧠 LLM Model: {settings.llm_model}")
    logger.info(f"🌍 Default City: {settings.default_city}")

    # P-011: 메모리 시스템 초기화
    logger.info("🧠 메모리 시스템 초기화 중...")
    memory_manager = MemoryManager(db_path="data/memory.db")
    logger.info("✅ 메모리 시스템 초기화 완료")

    # P-014: OAuth 시스템 초기화
    logger.info("🔐 OAuth 시스템 초기화 중...")
    encryption_key = os.getenv("ENCRYPTION_KEY")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    oauth_redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8080/oauth/callback")

    token_repository = TokenRepository(
        db_path="data/auth.db",
        encryption_key=encryption_key,
    )

    oauth_service = OAuthService(
        token_repository=token_repository,
        google_client_id=google_client_id,
        google_client_secret=google_client_secret,
        redirect_uri=oauth_redirect_uri,
    )

    # 토큰 갱신 스케줄러
    token_scheduler = TokenRefreshScheduler(
        token_repository=token_repository,
        oauth_service=oauth_service,
        check_interval_minutes=5,
    )
    token_scheduler.start()
    logger.info("✅ OAuth 시스템 초기화 완료")

    # OAuth 콜백 서버 시작 (8080 포트)
    if google_client_id:
        logger.info("🌐 OAuth 콜백 서버 시작 (포트: 8080)...")
        start_oauth_server(oauth_service, port=8080)
        logger.info("✅ OAuth 콜백 서버 시작됨")
    else:
        logger.warning("⚠️ GOOGLE_CLIENT_ID 미설정, OAuth 서버 비활성화")

    # AI 서비스 초기화
    logger.info("🧠 AI 서비스 초기화 중...")
    ai_service = AIService(
        api_key=settings.openai_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        assistant_name=settings.assistant_name,
        weather_api_key=settings.openweathermap_api_key,
        default_city=settings.default_city,
        kakao_api_key=settings.kakao_rest_api_key or None,
    )

    # 메시지 콜백 생성
    message_callback = create_message_callback(ai_service)

    # Slack Bot 초기화 (P-011: 메모리 매니저 연동)
    logger.info("🔌 Slack Bot 연결 중...")
    slack_handler = SlackHandler(
        bot_token=settings.slack_bot_token,
        app_token=settings.slack_app_token,
        message_callback=message_callback,
        memory_manager=memory_manager,
    )

    # P-014: Slack OAuth 명령어 등록
    logger.info("📎 OAuth 명령어 등록 중...")
    oauth_commands = SlackOAuthCommands(
        oauth_service=oauth_service,
        token_repository=token_repository,
    )

    oauth_commands.register_commands(slack_handler.app)
    logger.info("✅ OAuth 명령어 등록 완료 (/connect, /disconnect, /accounts)")

    # 스케줄러 초기화
    logger.info("⏰ 스케줄러 초기화 중...")
    scheduler = SchedulerService()

    # AIService에 스케줄러 연동 (리마인더 기능용)
    ai_service.set_scheduler(scheduler, slack_handler.send_message)
    logger.info("🔗 리마인더 기능 활성화됨")

    # 스케줄러 시작
    scheduler.start()
    logger.info(f"⏰ 스케줄러 시작됨 (등록된 작업: {len(scheduler.list_jobs())}개)")

    logger.info("✅ 모든 서비스 준비 완료!")
    logger.info("💬 메시지를 기다리는 중... (Ctrl+C로 종료)")

    # 봇 시작 (blocking)
    try:
        slack_handler.start()
    except KeyboardInterrupt:
        logger.info(f"👋 {settings.assistant_name} 종료...")
        scheduler.stop()
        token_scheduler.stop()
        token_repository.close()
        memory_manager.close()


if __name__ == "__main__":
    main()
