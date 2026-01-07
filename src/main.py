from contextlib import asynccontextmanager
from fastapi import FastAPI
from arq import create_pool
from arq.connections import RedisSettings

from src.config.settings import Settings
from src.presentation.api.routers import slack, auth

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create Redis Pool
    try:
        from urllib.parse import urlparse
        parsed = urlparse(settings.redis_url)
        redis_settings = RedisSettings(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 6379
        )
        app.state.arq_pool = await create_pool(redis_settings)
        print("ARQ Pool Created")
    except Exception as e:
        print(f"Failed to create ARQ pool: {e}")
    
    yield
    
    # Shutdown: Close Pool
    if hasattr(app.state, 'arq_pool'):
        await app.state.arq_pool.close()
        print("ARQ Pool Closed")


app = FastAPI(title="Panager", version="0.1.0", lifespan=lifespan)

# Register Routers
app.include_router(slack.router)
app.include_router(auth.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.env}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
