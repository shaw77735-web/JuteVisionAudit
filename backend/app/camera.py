"""Camera + YOLO inference engine for JuteVision."""
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from typing import Generator
from pathlib import Path

# Find model: backend/app/ -> JuteVision root
_model_path = Path(__file__).resolve().parent.parent.parent / "yolo11n.pt"
if not _model_path.exists():
    _model_path = "yolo11n.pt"  # fallback (downloads if needed)
else:
    _model_path = str(_model_path)

# Initialize once at module load
device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO(_model_path)

# Global camera instance (single capture)
cap: cv2.VideoCapture | None = None


def get_camera():
    """Get or create camera capture."""
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def release_camera():
    """Release camera resources."""
    global cap
    if cap is not None:
        cap.release()
        cap = None


def generate_frames() -> Generator[bytes, None, None]:
    """Generate MJPEG frames for streaming."""
    camera = get_camera()
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        results = model(frame, device=device, conf=0.5, verbose=False)
        annotated = results[0].plot()
        _, buffer = cv2.imencode(".jpg", annotated)
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


def get_detection_metrics() -> dict:
    """
    Process one frame and return metrics for weight estimation.
    Weight heuristic: base + (detection density * factor).
    Real implementation would use jute-specific model.
    """
    camera = get_camera()
    ret, frame = camera.read()
    if not ret:
        return {"weight_kg": 0, "detection_count": 0, "confidence": 0}

    results = model(frame, device=device, conf=0.5, verbose=False)[0]
    boxes = results.boxes
    n = len(boxes) if boxes is not None else 0

    # Heuristic: COCO detects objects; jute bales/bags correlate with object density
    # Placeholder formula - replace with real jute weight model
    base_kg = 12.5
    per_detection_kg = 3.2
    weight_kg = round(base_kg + (n * per_detection_kg), 1)

    # Confidence based on detection stability (simplified)
    conf = min(0.95, 0.4 + (n * 0.1)) if n > 0 else 0.35

    return {
        "weight_kg": weight_kg,
        "detection_count": n,
        "confidence": round(conf, 2),
    }


def process_uploaded_image(image_bytes: bytes) -> tuple[bytes, dict]:
    """Run YOLO on uploaded image, return annotated JPEG bytes + metrics."""
    arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Invalid image")
    results = model(frame, device=device, conf=0.5, verbose=False)[0]
    annotated = results.plot()
    _, buffer = cv2.imencode(".jpg", annotated)
    boxes = results.boxes
    n = len(boxes) if boxes is not None else 0
    weight_kg = round(12.5 + (n * 3.2), 1)
    conf = min(0.95, 0.4 + (n * 0.1)) if n > 0 else 0.35
    metrics = {"weight_kg": weight_kg, "detection_count": n, "confidence": round(conf, 2)}
    return buffer.tobytes(), metrics


def capture_frame() -> tuple[bytes | None, dict]:
    """Capture one frame, run YOLO, return annotated bytes + metrics."""
    camera = get_camera()
    ret, frame = camera.read()
    if not ret:
        return None, {"weight_kg": 0, "detection_count": 0, "confidence": 0}
    results = model(frame, device=device, conf=0.5, verbose=False)[0]
    annotated = results.plot()
    _, buffer = cv2.imencode(".jpg", annotated)
    boxes = results.boxes
    n = len(boxes) if boxes is not None else 0
    weight_kg = round(12.5 + (n * 3.2), 1)
    conf = min(0.95, 0.4 + (n * 0.1)) if n > 0 else 0.35
    metrics = {"weight_kg": weight_kg, "detection_count": n, "confidence": round(conf, 2)}
    return buffer.tobytes(), metrics
