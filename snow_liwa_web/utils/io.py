from __future__ import annotations
from pathlib import Path
import pandas as pd
from core.config import DATA_DIR, BOOKINGS_FILE

COLUMNS = [
    "booking_id","created_at","name","phone","tickets","ticket_price","total_amount","status",
    "payment_intent_id","payment_status","redirect_url","notes"
]

def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not BOOKINGS_FILE.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(BOOKINGS_FILE, index=False)


def load_bookings() -> pd.DataFrame:
    ensure_data_file()
    return pd.read_excel(BOOKINGS_FILE)


def save_bookings(df: pd.DataFrame) -> None:
    df.to_excel(BOOKINGS_FILE, index=False)
