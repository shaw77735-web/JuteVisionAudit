"""JuteVision FastAPI Backend - Production-ready business app."""
import base64
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from app.camera import generate_frames, get_detection_metrics, release_camera, process_uploaded_image, capture_frame
from app.settings import (
    ensure_saves_dir,
    get_settings,
    set_app_pin,
    set_app_pin_enabled,
    set_file_pin,
    set_file_pin_enabled,
    verify_app_pin,
    verify_file_pin,
)

# Audit state (shared)
audit_status = "idle"
total_jute_scanned_kg = 0.0


@asynccontextmanager
async def _lifespan(app: FastAPI):
    yield
    release_camera()


app = FastAPI(
    title="JuteVision Auditor",
    version="1.0",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve frontend when built (single URL for desktop + phone)
_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")
    from fastapi.responses import FileResponse
    @app.get("/")
    async def root():
        return FileResponse(_dist / "index.html")
else:
    @app.get("/")
    async def root():
        return {"app": "JuteVision Auditor", "status": "online"}


@app.get("/api/status")
async def get_status():
    """Return audit status and system health."""
    return {"audit_status": audit_status}


@app.post("/api/audit/start")
async def start_audit():
    """Start audit session."""
    global audit_status, total_jute_scanned_kg
    audit_status = "scanning"
    total_jute_scanned_kg = 0.0
    return {"audit_status": audit_status}


@app.post("/api/audit/stop")
async def stop_audit():
    """Stop audit session."""
    global audit_status
    audit_status = "complete"
    return {"audit_status": audit_status}


@app.post("/api/audit/reset")
async def reset_audit():
    """Reset session: clear total, set status to idle."""
    global audit_status, total_jute_scanned_kg
    audit_status = "idle"
    total_jute_scanned_kg = 0.0
    return {"audit_status": audit_status, "total_jute_scanned_kg": 0}


def _audit_progress() -> int:
    """Return 0-100 progress based on status."""
    mapping = {"idle": 0, "scanning": 45, "analyzing": 75, "complete": 100, "error": 0}
    return mapping.get(audit_status, 0)


@app.get("/api/metrics")
async def get_metrics():
    """Get estimated jute weight, audit progress, and total scanned."""
    global total_jute_scanned_kg
    metrics = get_detection_metrics()
    if audit_status == "scanning" or audit_status == "analyzing":
        total_jute_scanned_kg += metrics["weight_kg"] * 0.01  # accumulate per poll
    return {
        "estimated_weight_kg": metrics["weight_kg"],
        "detection_count": metrics["detection_count"],
        "confidence": metrics["confidence"],
        "audit_status": audit_status,
        "audit_progress": _audit_progress(),
        "total_jute_scanned_kg": round(total_jute_scanned_kg, 1),
    }


@app.get("/video_feed")
async def video_feed():
    """Stream live camera feed with YOLO overlay (MJPEG)."""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# --- Upload, Capture, Save ---


@app.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...),
    save: bool = Form(False),
    file_pin: str = Form(""),
):
    """Upload image, run YOLO, return annotated result. Optionally save."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    data = await file.read()
    annotated_bytes, metrics = process_uploaded_image(data)
    b64 = base64.b64encode(annotated_bytes).decode()
    result = {"annotated_base64": b64, "metrics": metrics}
    if save:
        if get_settings().get("file_pin_enabled") and not verify_file_pin(file_pin):
            raise HTTPException(403, "Invalid file access PIN")
        save_dir = ensure_saves_dir()
        fname = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        path = save_dir / fname
        path.write_bytes(annotated_bytes)
        result["saved_as"] = fname
    return result


@app.post("/api/capture")
async def capture_and_save(
    file_pin: str = Form(""),
):
    """Capture current frame, save to disk, return filename."""
    if get_settings().get("file_pin_enabled") and not verify_file_pin(file_pin):
        raise HTTPException(403, "Invalid file access PIN")
    img_bytes, metrics = capture_frame()
    if img_bytes is None:
        raise HTTPException(503, "Could not capture frame")
    save_dir = ensure_saves_dir()
    fname = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = save_dir / fname
    path.write_bytes(img_bytes)
    return {"saved_as": fname, "metrics": metrics}


@app.get("/api/saved")
async def list_saved(file_pin: str = ""):
    """List saved images. Requires file PIN if enabled."""
    if get_settings().get("file_pin_enabled") and not verify_file_pin(file_pin):
        raise HTTPException(403, "Invalid file access PIN")
    save_dir = ensure_saves_dir()
    files = sorted(
        [f.name for f in save_dir.glob("*.jpg")],
        key=lambda n: (save_dir / n).stat().st_mtime,
        reverse=True,
    )
    return {"files": files}


@app.get("/api/saved/{filename}")
async def get_saved(filename: str, file_pin: str = ""):
    """Download a saved image."""
    if get_settings().get("file_pin_enabled") and not verify_file_pin(file_pin):
        raise HTTPException(403, "Invalid file access PIN")
    save_dir = ensure_saves_dir()
    path = save_dir / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="image/jpeg")


# --- Settings & PIN ---


@app.get("/api/settings")
async def api_get_settings():
    """Get app settings (PIN enabled flags only, no hashes)."""
    s = get_settings()
    return {
        "app_pin_enabled": s.get("app_pin_enabled", False),
        "file_pin_enabled": s.get("file_pin_enabled", False),
    }


@app.post("/api/settings/app_pin")
async def api_set_app_pin(enabled: bool = Form(...), pin: str = Form("")):
    """Enable/disable app PIN. If enabling, pin is required."""
    if enabled and not pin:
        raise HTTPException(400, "PIN required when enabling")
    set_app_pin_enabled(enabled)
    if enabled:
        set_app_pin(pin)
    return {"app_pin_enabled": enabled}


@app.post("/api/settings/file_pin")
async def api_set_file_pin(enabled: bool = Form(...), pin: str = Form("")):
    """Enable/disable file access PIN. If enabling, pin is required."""
    if enabled and not pin:
        raise HTTPException(400, "PIN required when enabling")
    set_file_pin_enabled(enabled)
    if enabled:
        set_file_pin(pin)
    return {"file_pin_enabled": enabled}


@app.post("/api/verify_pin")
async def api_verify_pin(pin_type: str = Form(...), pin: str = Form(...)):
    """Verify app or file PIN."""
    if pin_type == "app":
        ok = verify_app_pin(pin)
    elif pin_type == "file":
        ok = verify_file_pin(pin)
    else:
        raise HTTPException(400, "pin_type must be 'app' or 'file'")
    return {"valid": ok}
