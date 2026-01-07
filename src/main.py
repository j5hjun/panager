from fastapi import FastAPI
from src.config.settings import Settings

app = FastAPI(title="Panager", version="0.1.0")
settings = Settings()

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.env}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
