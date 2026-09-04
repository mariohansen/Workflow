from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.routes.health import router as health_router
from app.api.routes.workflows import router as workflows_router
from app.settings import get_settings


def create_app() -> FastAPI:
    app = FastAPI(title="Workflow Studio")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(workflows_router)
    register_error_handlers(app)
    return app


app = create_app()
