from __future__ import annotations
from datetime import datetime
import pandas as pd
from core.config import TICKET_PRICE_AED
from utils.io import load_bookings, save_bookings


def get_next_booking_id(df: pd.DataFrame) -> str:
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"SL-{today}-"
    todays = df[df["booking_id"].astype(str).str.startswith(prefix)]
    if todays.empty:
        seq = 1
    else:
        last = todays["booking_id"].iloc[-1]
        try:
            seq = int(str(last).split("-")[-1]) + 1
        except Exception:
            seq = len(todays) + 1
    return prefix + f"{seq:03d}"


def create_booking_and_get_amount(form_data: dict) -> tuple[str, float]:
    """Create a booking row and return (booking_id, total_amount)."""
    df = load_bookings()
    booking_id = get_next_booking_id(df)
    tickets = int(form_data.get("tickets") or form_data.get("people_count") or 1)
    total_amount = float(tickets) * TICKET_PRICE_AED
    new_row = {
        "booking_id": booking_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": form_data.get("name") or form_data.get("customer_name") or "",
        "phone": form_data.get("phone") or "",
        "tickets": tickets,
        "ticket_price": TICKET_PRICE_AED,
        "total_amount": total_amount,
        "status": "pending",
        "payment_intent_id": None,
        "payment_status": "pending",
        "redirect_url": None,
        "notes": form_data.get("notes") or "",
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_bookings(df)
    return booking_id, total_amount
