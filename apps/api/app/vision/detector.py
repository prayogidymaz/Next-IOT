"""YOLOv8 pest detector with mock fallback."""

from __future__ import annotations

import logging
import random
from pathlib import Path

from app.vision.schemas import BoundingBox, DetectionResult, PestLabel

logger = logging.getLogger(__name__)

_INDONESIAN_PEST_LABELS: tuple[str, ...] = (
    PestLabel.SPODOPTERA.value,
    PestLabel.APHID.value,
    PestLabel.MITE.value,
    PestLabel.WHITEFLY.value,
    PestLabel.NONE.value,
)


class PestDetector:
    def __init__(self, model_path: str = "models/yolov8n-pest.pt", confidence_threshold: float = 0.5) -> None:
        self._model_path = Path(model_path)
        self._confidence_threshold = confidence_threshold
        self._model: object | None = None
        if self._model_path.is_file():
            self._model = self._load_yolo()

    def _load_yolo(self) -> object | None:
        try:
            from ultralytics import YOLO
        except ImportError:
            logger.warning("ultralytics not installed; using mock pest detector")
            return None
        try:
            return YOLO(str(self._model_path))
        except Exception:
            logger.exception("Failed to load YOLO model at %s", self._model_path)
            return None

    @property
    def uses_mock(self) -> bool:
        return self._model is None

    def detect(self, image_bytes: bytes) -> DetectionResult:
        if self._model is not None:
            parsed = self._detect_yolo(image_bytes)
            if parsed is not None:
                return parsed
        return self._detect_mock(image_bytes)

    def _detect_yolo(self, image_bytes: bytes) -> DetectionResult | None:
        predict = getattr(self._model, "predict", None)
        if predict is None:
            return None
        try:
            results = predict(source=image_bytes, verbose=False)
        except Exception:
            logger.exception("YOLO predict failed")
            return None
        if not results:
            return self._empty_result()
        result0 = results[0]
        boxes_obj = getattr(result0, "boxes", None)
        if boxes_obj is None:
            return self._empty_result()
        bboxes: list[BoundingBox] = []
        labels: list[str] = []
        confidences: list[float] = []
        names = getattr(result0, "names", {}) or {}
        xyxy = getattr(boxes_obj, "xyxy", None)
        cls = getattr(boxes_obj, "cls", None)
        conf = getattr(boxes_obj, "conf", None)
        if xyxy is None or cls is None or conf is None:
            return self._empty_result()
        for idx in range(len(xyxy)):
            row = xyxy[idx].tolist()
            x1, y1, x2, y2 = (float(row[0]), float(row[1]), float(row[2]), float(row[3]))
            score = float(conf[idx])
            if score < self._confidence_threshold:
                continue
            class_id = int(cls[idx])
            label = str(names.get(class_id, PestLabel.NONE.value))
            bboxes.append(BoundingBox(x=x1, y=y1, w=x2 - x1, h=y2 - y1))
            labels.append(label)
            confidences.append(score)
        if not confidences:
            return self._empty_result()
        species = labels[0] if labels else PestLabel.NONE.value
        return DetectionResult(
            bboxes=bboxes,
            labels=labels,
            confidences=confidences,
            species_guess=species,
            max_confidence=max(confidences),
        )

    def _detect_mock(self, image_bytes: bytes) -> DetectionResult:
        seed = sum(image_bytes[:64]) if image_bytes else 42
        rng = random.Random(seed)
        label = rng.choice(_INDONESIAN_PEST_LABELS)
        if label == PestLabel.NONE.value:
            return self._empty_result()
        confidence = round(rng.uniform(0.45, 0.97), 3)
        if confidence < self._confidence_threshold:
            return self._empty_result()
        bbox = BoundingBox(
            x=round(rng.uniform(0.1, 0.5), 3),
            y=round(rng.uniform(0.1, 0.5), 3),
            w=round(rng.uniform(0.1, 0.3), 3),
            h=round(rng.uniform(0.1, 0.3), 3),
        )
        return DetectionResult(
            bboxes=[bbox],
            labels=[label],
            confidences=[confidence],
            species_guess=label,
            max_confidence=confidence,
        )

    @staticmethod
    def _empty_result() -> DetectionResult:
        return DetectionResult(
            bboxes=[],
            labels=[PestLabel.NONE.value],
            confidences=[0.0],
            species_guess=PestLabel.NONE.value,
            max_confidence=0.0,
        )
