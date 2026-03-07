"""FastAPI backend for HART-Morphosis enterprise image generation service.

Endpoints:
    GET  /health          — liveness probe
    POST /generate        — generate an image from a text prompt

Features:
    - CORS configured for the Next.js UI (port 3000 by default)
    - Per-IP rate limiting (configurable via RATE_LIMIT_PER_MINUTE env var)
    - Structured JSON request logging
    - All errors return JSON { "detail": "..." }
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Ensure project root is on sys.path when running from the api/ directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.hart_morphosis.core import (  # noqa: E402
    HART,
    FractalRenderer,
    MorphogenesisEngine,
    PromptEncoder,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "msg": %(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("hart_api")

# ---------------------------------------------------------------------------
# Rate limiter (in-memory, per client IP)
# ---------------------------------------------------------------------------

RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))

# Number of hex characters from the SHA-256 digest to use as a numeric seed.
# 8 hex chars = 32-bit integer, sufficient for RNG seeding while staying
# within Python's int range without wrapping issues.
_SEED_HASH_HEX_CHARS = 8
_rate_store: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    window = 60.0
    requests = _rate_store[client_ip]
    # Remove entries older than the window
    _rate_store[client_ip] = [t for t in requests if now - t < window]
    if len(_rate_store[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests/minute.",
        )
    _rate_store[client_ip].append(now)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="HART-Morphosis API",
    description="Enterprise-grade image generation via morphogenesis and fractal rendering.",
    version="1.0.0",
)

# CORS — allow the Next.js dev server and any configured production origin
_cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared prompt encoder (stateless, safe to reuse)
_encoder = PromptEncoder()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500, description="Text prompt")
    zoom: int = Field(default=2, ge=1, le=6, description="Fractal zoom level (1–6)")
    seed: Optional[int] = Field(default=None, description="Optional RNG seed")


class GenerateResponse(BaseModel):
    image_b64: str = Field(..., description="Base-64 encoded PNG image")
    width: int
    height: int
    seed: int
    prompt: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _prompt_to_seed(prompt: str) -> int:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return int(digest[:_SEED_HASH_HEX_CHARS], 16)


def _generate(prompt: str, zoom: int, seed: Optional[int]) -> GenerateResponse:
    t0 = time.monotonic()

    params = _encoder.encode(prompt)

    resolved_seed = (seed if seed is not None else _prompt_to_seed(prompt)) + params.seed_offset
    torch.manual_seed(resolved_seed)

    morpho = MorphogenesisEngine(
        grid_size=params.morphogenesis.grid_size,
        device="cpu",
    )
    pattern = morpho.generate_pattern(
        steps=params.morphogenesis.steps,
        seed=resolved_seed,
    )

    # Build base_state: [1, H, W, d_model]
    base_state = pattern.unsqueeze(-1).repeat(1, 1, params.d_model).unsqueeze(0)

    model = HART(d_model=params.d_model, num_layers=params.num_layers)
    with torch.no_grad():
        refined = model(base_state).squeeze(0)

    renderer = FractalRenderer(base_resolution=params.rendering.base_resolution)
    effective_zoom = zoom  # caller's zoom takes precedence over prompt-derived default
    zoomed = renderer.render_zoom_level(refined, zoom_level=effective_zoom)
    pil_image = renderer.tensor_to_pil(zoomed)

    # Encode to base64 PNG
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    latency_ms = (time.monotonic() - t0) * 1000

    return GenerateResponse(
        image_b64=image_b64,
        width=pil_image.width,
        height=pil_image.height,
        seed=resolved_seed,
        prompt=prompt,
        latency_ms=round(latency_ms, 1),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["infra"])
async def health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse()


@app.post("/generate", response_model=GenerateResponse, tags=["generation"])
async def generate(body: GenerateRequest, request: Request) -> GenerateResponse:
    """Generate an image from a text prompt.

    Returns a JSON payload with the base-64 encoded PNG and metadata.
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    logger.info(
        '"generate" prompt=%r zoom=%d seed=%s client=%s',
        body.prompt,
        body.zoom,
        body.seed,
        client_ip,
    )

    try:
        result = _generate(body.prompt, body.zoom, body.seed)
    except Exception as exc:  # pragma: no cover
        logger.error('"generate_error" error=%r', str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    logger.info(
        '"generate_ok" latency_ms=%.1f width=%d height=%d seed=%d',
        result.latency_ms,
        result.width,
        result.height,
        result.seed,
    )
    return result
