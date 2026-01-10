from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import RequestLoggingMiddleware

import asyncio
from contextlib import asynccontextmanager
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from app.api.routes import auth, webhooks
from app.core.slack import slack_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start generic async task for Slack Socket Mode
    # WARNING: In production, you might want to run this as a separate process/worker
    # instead of inside the same event loop as FastAPI.
    # But for MVP, this is fine.

    # Check if app token is set (it might be dummy in CI/test)
    if settings.SLACK_APP_TOKEN and "xapp" in settings.SLACK_APP_TOKEN:
        handler = AsyncSocketModeHandler(slack_app, settings.SLACK_APP_TOKEN)
        # Run in background
        _ = asyncio.create_task(handler.start_async())
        yield
        # Shutdown logic if needed (handler doesn't have stop properly exposed in easy way?)
    else:
        yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(webhooks.router, prefix="/api/v1/webhook", tags=["webhooks"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "Proactive Manager API is running"}
