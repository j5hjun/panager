from arq.connections import RedisSettings
from src.infrastructure.container import Container
from src.infrastructure.db import get_db

async def startup(ctx):
    """Worker 시작 시 실행"""
    container = Container.get_instance()
    ctx['container'] = container
    print("Worker started")

async def shutdown(ctx):
    """Worker 종료 시 실행"""
    print("Worker shutdown")


async def handle_slack_event(ctx, event_data: dict):
    """
    Slack Event 처리 작업
    """
    print(f"Received slack event: {event_data}")
    
    text = event_data.get('text', '')
    user_id = event_data.get('user')
    
    # 봇 메시지 무시
    if event_data.get('bot_id'):
        return

    # Container
    container = ctx['container']
    
    # DB Session Context
    async for session in get_db():
        auth_service = container.get_auth_service(session)
        noti_service = container.get_notification_service() # Session 불필요
        
        try:
            # 1. 로그인/연결 요청
            if "로그인" in text or "연결" in text:
                auth_url = auth_service.generate_auth_url(user_id)
                await noti_service.send_message(
                    user_id, 
                    f"🔗 아래 링크를 클릭하여 Google 계정을 연결해주세요:\n{auth_url}"
                )
            
            # 2. 그 외 메시지
            else:
                await noti_service.send_message(
                    user_id,
                    "아직 배우는 중입니다. '로그인' 또는 '연결'이라고 말해보세요. 😅"
                )
        except Exception as e:
            print(f"Error handling event: {e}")
            await noti_service.send_message(user_id, "오류가 발생했습니다.")
        
        # Loop break (since get_db yields once)
        break


# 동적 설정 로드
try:
    from src.config.settings import Settings
    settings = Settings()
    redis_url = settings.redis_url
    # redis://host:port 파싱 (arq는 RedisSettings 객체 필요)
    # 간단히 host, port만 추출하거나 arq.connections.RedisSettings.from_dsn 사용
    from urllib.parse import urlparse
    parsed = urlparse(redis_url)
    redis_host = parsed.hostname or 'localhost'
    redis_port = parsed.port or 6379
except Exception:
    redis_host = 'localhost'
    redis_port = 6379


class WorkerSettings:
    functions = [handle_slack_event]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(host=redis_host, port=redis_port)
