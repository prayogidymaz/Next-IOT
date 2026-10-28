"""Vision pipeline tests."""

from __future__ import annotations

import base64
import uuid

import pytest
from httpx import AsyncClient

from app.vision.confidence_router import ConfidenceRouter
from app.vision.detector import PestDetector
from app.vision.feedback_loop import FalsePositiveFeedback, compute_adjusted_threshold
from app.vision.schemas import DetectionResult, RoutingAction
PASSWORD = "SecurePass123!"


def test_detector_mock_fallback() -> None:
    detector = PestDetector(model_path="models/missing.pt", confidence_threshold=0.4)
    assert detector.uses_mock
    result = detector.detect(b"fake-image-bytes-for-mock")
    assert result.species_guess in {"spodoptera", "aphid", "mite", "whitefly", "none"}


def test_detector_confidence_filter() -> None:
    detector = PestDetector(confidence_threshold=0.99)
    result = detector.detect(b"x" * 128)
    assert result.max_confidence == 0.0 or result.max_confidence >= 0.99


def test_confidence_router_high_auto_trigger() -> None:
    result = DetectionResult(
        bboxes=[],
        labels=["aphid"],
        confidences=[0.9],
        species_guess="aphid",
        max_confidence=0.9,
    )
    decision = ConfidenceRouter().route(result, uuid.uuid4(), uuid.uuid4())
    assert decision.action == RoutingAction.AUTO_TRIGGER


def test_confidence_router_medium_review() -> None:
    result = DetectionResult(
        bboxes=[],
        labels=["mite"],
        confidences=[0.7],
        species_guess="mite",
        max_confidence=0.7,
    )
    decision = ConfidenceRouter().route(result, uuid.uuid4(), uuid.uuid4())
    assert decision.action == RoutingAction.HUMAN_REVIEW


def test_confidence_router_low_log_only() -> None:
    result = DetectionResult(
        bboxes=[],
        labels=["none"],
        confidences=[0.4],
        species_guess="none",
        max_confidence=0.4,
    )
    decision = ConfidenceRouter().route(result, uuid.uuid4(), uuid.uuid4())
    assert decision.action == RoutingAction.LOG_ONLY


def test_feedback_loop_adjusts_threshold() -> None:
    assert compute_adjusted_threshold(0.5, 0.2) == 0.55
    assert compute_adjusted_threshold(0.5, 0.02) == 0.47
    assert FalsePositiveFeedback.ADJUSTMENT_WINDOW == 100


@pytest.mark.asyncio
async def test_vision_endpoints_require_auth(client: AsyncClient) -> None:
    assert (await client.post("/api/v1/vision/detect", json={"image_base64": "abc", "device_id": str(uuid.uuid4())})).status_code == 401


async def _token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Vision", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_detection_endpoint_full_flow(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    device_resp = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "cam-1", "device_type": "vision_camera", "device_category": "field_sensors_lora"},
    )
    assert device_resp.status_code == 201
    device_id = device_resp.json()["device"]["id"]
    img = base64.b64encode(b"pest-image-sample-bytes").decode()
    resp = await client.post(
        "/api/v1/vision/detect",
        headers={"Authorization": f"Bearer {token}"},
        json={"image_base64": img, "device_id": device_id},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["detection_id"]
    assert body["routing"]["action"]


def test_routing_severity_levels() -> None:
    high = ConfidenceRouter().route(
        DetectionResult(bboxes=[], labels=["a"], confidences=[0.9], species_guess="aphid", max_confidence=0.9),
        uuid.uuid4(),
        uuid.uuid4(),
    )
    assert high.severity == "high"


def test_detector_labels_indonesia_pest_set() -> None:
    labels = set()
    for seed in range(20):
        res = PestDetector(confidence_threshold=0.3).detect(bytes([seed]) * 32)
        labels.add(res.species_guess)
    assert labels.issubset({"spodoptera", "aphid", "mite", "whitefly", "none"})


def test_mock_detection_has_bbox_when_pest() -> None:
    found_bbox = False
    for seed in range(30):
        res = PestDetector(confidence_threshold=0.3).detect(bytes([seed + 1]) * 64)
        if res.species_guess != "none":
            found_bbox = len(res.bboxes) >= 1
            break
    assert found_bbox


@pytest.mark.asyncio
async def test_vision_stats_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    resp = await client.get("/api/v1/vision/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "precision" in resp.json()


@pytest.mark.asyncio
async def test_vision_detections_list(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    resp = await client.get("/api/v1/vision/detections", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_vision_feedback_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    device_resp = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "cam-2", "device_type": "vision_camera", "device_category": "field_sensors_lora"},
    )
    device_id = device_resp.json()["device"]["id"]
    img = base64.b64encode(b"feedback-test-image").decode()
    detect = await client.post(
        "/api/v1/vision/detect",
        headers={"Authorization": f"Bearer {token}"},
        json={"image_base64": img, "device_id": device_id},
    )
    detection_id = detect.json()["detection_id"]
    fb = await client.post(
        f"/api/v1/vision/{detection_id}/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={"verdict": "true_positive", "notes": "confirmed"},
    )
    assert fb.status_code == 200
