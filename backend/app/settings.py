"""Settings and PIN storage for JuteVision."""
import hashlib
import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent.parent / "jutevision_settings.json"
SAVES_DIR = Path(__file__).resolve().parent.parent.parent / "saved_images"

DEFAULTS = {
    "app_pin_enabled": False,
    "file_pin_enabled": False,
    "app_pin_hash": "",
    "file_pin_hash": "",
}


def _load() -> dict:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                return {**DEFAULTS, **data}
        except Exception:
            pass
    return DEFAULTS.copy()


def _save(data: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def get_settings() -> dict:
    return _load()


def set_app_pin_enabled(enabled: bool) -> None:
    d = _load()
    d["app_pin_enabled"] = enabled
    _save(d)


def set_file_pin_enabled(enabled: bool) -> None:
    d = _load()
    d["file_pin_enabled"] = enabled
    _save(d)


def set_app_pin(pin: str) -> None:
    d = _load()
    d["app_pin_hash"] = _hash_pin(pin)
    d["app_pin_enabled"] = True
    _save(d)


def set_file_pin(pin: str) -> None:
    d = _load()
    d["file_pin_hash"] = _hash_pin(pin)
    d["file_pin_enabled"] = True
    _save(d)


def verify_app_pin(pin: str) -> bool:
    d = _load()
    if not d["app_pin_enabled"] or not d["app_pin_hash"]:
        return True
    return d["app_pin_hash"] == _hash_pin(pin)


def verify_file_pin(pin: str) -> bool:
    d = _load()
    if not d["file_pin_enabled"] or not d["file_pin_hash"]:
        return True
    return d["file_pin_hash"] == _hash_pin(pin)


def ensure_saves_dir() -> Path:
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    return SAVES_DIR
