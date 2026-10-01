from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

app = FastAPI(
    title=settings.app_name,
    description="AI-powered personalized comic story generator",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.environment,
    }