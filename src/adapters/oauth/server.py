"""
FastAPI OAuth 콜백 서버

OAuth 인증 콜백을 처리하는 경량 웹서버입니다.
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)


def create_oauth_app(oauth_service: Any) -> FastAPI:
    """
    OAuth 콜백 처리용 FastAPI 앱 생성

    Args:
        oauth_service: OAuthService 인스턴스

    Returns:
        FastAPI 앱
    """
    app = FastAPI(
        title="Panager OAuth",
        description="OAuth 콜백 처리 서버",
        docs_url=None,  # 문서 비활성화
        redoc_url=None,
    )

    @app.get("/health")
    async def health_check():
        """헬스 체크"""
        return {"status": "ok"}

    @app.get("/oauth/callback", response_class=HTMLResponse)
    async def oauth_callback(
        code: str | None = Query(default=None),
        state: str | None = Query(default=None),
        error: str | None = Query(default=None),
        error_description: str | None = Query(default=None),
    ):
        """
        OAuth 콜백 엔드포인트

        Google/iCloud OAuth 인증 완료 후 리다이렉트되는 엔드포인트입니다.
        """
        # 에러 응답 처리
        if error:
            logger.warning(f"OAuth 에러: {error} - {error_description}")
            raise HTTPException(
                status_code=400,
                detail=f"OAuth 인증 실패: {error_description or error}",
            )

        # 필수 파라미터 확인
        if not code or not state:
            raise HTTPException(
                status_code=400,
                detail="Missing code or state parameter",
            )

        # state 검증
        state_data = oauth_service.get_state_data(state)
        if not state_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired state",
            )

        provider = state_data.get("provider", "google")
        user_id = state_data.get("user_id")

        try:
            # 토큰 교환
            oauth_service.exchange_code(provider, code, state)

            logger.info(f"OAuth 연결 완료: {user_id}/{provider}")

            # 성공 HTML 응답
            return _success_html(provider)

        except Exception as e:
            logger.error(f"토큰 교환 실패: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"토큰 교환 실패: {str(e)}",
            ) from e

    return app


def _success_html(provider: str) -> str:
    """연결 성공 HTML 페이지"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>연결 완료</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 1rem;
                backdrop-filter: blur(10px);
            }}
            .success-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                margin: 0 0 1rem 0;
            }}
            p {{
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>{provider.title()} 계정 연결 완료!</h1>
            <p>이 창을 닫고 Slack으로 돌아가세요.</p>
            <p>패니저가 이제 캘린더에 접근할 수 있습니다.</p>
        </div>
    </body>
    </html>
    """


def _error_html(message: str) -> str:
    """에러 HTML 페이지"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>연결 실패</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 1rem;
                backdrop-filter: blur(10px);
            }}
            .error-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-icon">❌</div>
            <h1>연결 실패</h1>
            <p>{message}</p>
            <p>다시 시도해주세요.</p>
        </div>
    </body>
    </html>
    """
