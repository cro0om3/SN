from __future__ import annotations
import json
from pathlib import Path
from core.config import SETTINGS_FILE, DATA_DIR

DEFAULT_SETTINGS = {"ticket_poster_path": "assets/ticket_poster.png"}


def ensure_settings_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)


def load_settings() -> dict:
    ensure_settings_file()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
