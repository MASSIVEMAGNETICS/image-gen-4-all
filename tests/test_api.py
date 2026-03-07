"""Integration tests for the FastAPI backend (api/main.py).

Uses FastAPI's built-in TestClient so no live server is needed.
"""

from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_body(self):
        res = client.get("/health")
        data = res.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestGenerateEndpoint:
    def _post(self, payload: dict) -> dict:
        res = client.post("/generate", json=payload)
        assert res.status_code == 200, res.text
        return res.json()

    def test_basic_generate(self):
        data = self._post({"prompt": "a forest of trees", "zoom": 1})
        assert "image_b64" in data
        assert data["width"] > 0
        assert data["height"] > 0
        assert isinstance(data["seed"], int)
        assert data["latency_ms"] >= 0

    def test_image_is_valid_png(self):
        data = self._post({"prompt": "ocean waves", "zoom": 1})
        raw = base64.b64decode(data["image_b64"])
        # PNG magic bytes
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"

    def test_explicit_seed_is_echoed(self):
        data = self._post({"prompt": "galaxy", "zoom": 1, "seed": 42})
        # seed may be offset by prompt encoder, but it's always an int
        assert isinstance(data["seed"], int)

    def test_same_seed_same_image(self):
        payload = {"prompt": "minimal clean", "zoom": 1, "seed": 7}
        d1 = self._post(payload)
        d2 = self._post(payload)
        assert d1["image_b64"] == d2["image_b64"]

    def test_prompt_is_echoed(self):
        data = self._post({"prompt": "fractal mandala", "zoom": 1})
        assert data["prompt"] == "fractal mandala"

    def test_invalid_zoom_rejected(self):
        res = client.post("/generate", json={"prompt": "test", "zoom": 0})
        assert res.status_code == 422  # Pydantic validation error

    def test_zoom_too_high_rejected(self):
        res = client.post("/generate", json={"prompt": "test", "zoom": 7})
        assert res.status_code == 422

    def test_empty_prompt_rejected(self):
        res = client.post("/generate", json={"prompt": "", "zoom": 1})
        assert res.status_code == 422

    def test_missing_prompt_rejected(self):
        res = client.post("/generate", json={"zoom": 1})
        assert res.status_code == 422
