import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import STATIC, api, pages
from app.core.calculator import ChartService
from app.core.data_loader import load_database

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app):
    app.state.service = ChartService(load_database())
    yield


app = FastAPI(title="铁板神数", lifespan=lifespan, docs_url=None, redoc_url=None)
origins = [x for x in os.getenv("CORS_ORIGINS", "").split(",") if x]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(api)
app.include_router(pages)
app.mount("/static", StaticFiles(directory=STATIC), name="static")
