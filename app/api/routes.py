import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import ValidationError

from app.models.schemas import ChartRequest
from app.services.report_service import render_markdown

logger = logging.getLogger(__name__)
api = APIRouter(prefix="/api/v1")
pages = APIRouter()
STATIC = Path(__file__).resolve().parents[1] / "static"
_requests = defaultdict(deque)
_lock = asyncio.Lock()
_slots = asyncio.Semaphore(4)


def error(status, code, message):
    return JSONResponse(status_code=status, content={"success": False, "error": {"code": code, "message": message}})


async def limit(request):
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    async with _lock:
        hits = _requests[ip]
        while hits and hits[0] < now - 60:
            hits.popleft()
        if len(hits) >= int(os.getenv("RATE_LIMIT_PER_MINUTE", "20")):
            return False
        hits.append(now)
        # Bound memory for changing client IPs.
        if len(_requests) > 10000:
            for address in list(_requests):
                if not _requests[address] or _requests[address][-1] < now - 60:
                    del _requests[address]
    return True


async def compute(request, body):
    if not await limit(request):
        return error(429, "RATE_LIMITED", "请求过于频繁，请稍后再试")
    try:
        chart = ChartRequest.model_validate(body)
        gender = {"1": "男", "2": "女"}.get(chart.gender, chart.gender)
        async with _slots:
            result = await asyncio.wait_for(
                asyncio.to_thread(request.app.state.service.calculate, gender,
                                  chart.birth_datetime, chart.query_datetime),
                timeout=15,
            )
        return result
    except ValidationError:
        return error(422, "INVALID_INPUT", "请检查性别和日期时间格式")
    except ValueError as exc:
        return error(422, "INVALID_DATETIME", str(exc) if str(exc) else "日期时间无效")
    except asyncio.TimeoutError:
        logger.error("chart calculation timed out")
        return error(504, "TIMEOUT", "排盘超时，请稍后再试")
    except RuntimeError as exc:
        logger.exception("chart conversion or calculation failed")
        return error(503, "CALCULATION_FAILED", str(exc))
    except Exception:
        logger.exception("unexpected chart failure")
        return error(500, "INTERNAL_ERROR", "排盘暂时不可用，请稍后再试")


async def parse_json(request):
    try:
        if int(request.headers.get("content-length", "0")) > 4096:
            return None
        body = await request.body()
        if len(body) > 4096:
            return None
        return await request.json()
    except Exception:
        return None


@api.get("/health")
async def health(request: Request):
    return {"success": True, "data": {"status": "ok", "database_loaded": bool(request.app.state.service)}}


@api.post("/chart")
async def chart(request: Request):
    body = await parse_json(request)
    if body is None:
        return error(400, "INVALID_JSON", "请求内容不是有效 JSON，或超过大小限制")
    result = await compute(request, body)
    if isinstance(result, JSONResponse):
        return result
    return {"success": True, "data": result}


@api.post("/report.md")
async def markdown_report(request: Request):
    body = await parse_json(request)
    if body is None:
        return error(400, "INVALID_JSON", "请求内容不是有效 JSON，或超过大小限制")
    result = await compute(request, body)
    if isinstance(result, JSONResponse):
        return result
    report = render_markdown(result)
    return PlainTextResponse(report, media_type="text/markdown; charset=utf-8",
                             headers={"Content-Disposition": "attachment; filename=tiebanshenshu-report.md"})


@pages.get("/", response_class=HTMLResponse)
@pages.get("/result", response_class=HTMLResponse)
async def index():
    return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))


@pages.get("/about", response_class=HTMLResponse)
async def about():
    return HTMLResponse((STATIC / "about.html").read_text(encoding="utf-8"))
