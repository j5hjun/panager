"""
통합형 능동적 AI 비서 "패니저" - 메인 진입점

이 모듈은 애플리케이션의 시작점입니다.
"""

import asyncio
import logging
import sys

from src.adapters.slack.handler import SlackHandler
from src.config.settings import get_settings
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


def main() -> None:
    """애플리케이션 메인 함수"""
    setup_logging()
    logger = logging.getLogger(__name__)

    settings = get_settings()
    logger.info(f"🤵 {settings.assistant_name} AI 비서를 시작합니다...")
    logger.info(f"📡 LLM Provider: {settings.llm_provider}")
    logger.info(f"🧠 LLM Model: {settings.llm_model}")
    logger.info(f"🌍 Default City: {settings.default_city}")

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

    # Slack Bot 초기화
    logger.info("🔌 Slack Bot 연결 중...")
    slack_handler = SlackHandler(
        bot_token=settings.slack_bot_token,
        app_token=settings.slack_app_token,
        message_callback=message_callback,
    )

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


if __name__ == "__main__":
    main()
