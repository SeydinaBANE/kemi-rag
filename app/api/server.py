from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.logging import setup_logging

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kemi RAG Agent",
        version="0.1.0",
        description="Agent RAG avec LangGraph, OpenRouter, et pgvector",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app


app = create_app()
