from __future__ import annotations
from pathlib import Path
from typing import Tuple
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BOOKINGS_FILE = DATA_DIR / "bookings.xlsx"
SETTINGS_FILE = DATA_DIR / "settings.json"
ASSETS_DIR = BASE_DIR / "assets"
PAGES_DIR = BASE_DIR / "pages"

# Business constants
TICKET_PRICE_AED = int(os.getenv("TICKET_PRICE_AED", "175"))
ZIINA_API_BASE = os.getenv("ZIINA_API_BASE", "https://api-v2.ziina.com/api")

# Admin PIN
ADMIN_PIN = os.getenv("ADMIN_PIN", "change_me")

# External config

def get_ziina_config() -> Tuple[str | None, str, bool]:
    """Return (access_token, app_base_url, test_mode) from environment.
    - ZIINA_ACCESS_TOKEN: API token
    - ZIINA_APP_BASE_URL: Public base URL for redirect (defaults to http://localhost:8000)
    - ZIINA_TEST_MODE: "true" / "false"
    """
    access_token = os.getenv("ZIINA_ACCESS_TOKEN")
    app_base_url = os.getenv("ZIINA_APP_BASE_URL", "http://localhost:8000")
    test_mode = str(os.getenv("ZIINA_TEST_MODE", "false")).strip().lower() in ("1", "true", "yes", "on")
    return access_token, app_base_url, test_mode
