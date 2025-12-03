"""Ziina payment service layer - FastAPI port.
No Streamlit dependency; everything is pure logic.
"""
from __future__ import annotations
import logging
from typing import Optional
import requests
import pandas as pd
from core.config import get_ziina_config, ZIINA_API_BASE
from utils.io import load_bookings, save_bookings

# Public API ---------------------------------------------------------------

def has_ziina_configured() -> bool:
    access_token, _, _ = get_ziina_config()
    if not access_token:
        return False
    if isinstance(access_token, str) and (
        access_token.startswith("PUT_") 
        or access_token.startswith("REPLACE_")
        or access_token.startswith("YOUR_")
    ):
        return False
    return True


def create_payment_intent(amount_aed: float, booking_id: str, customer_name: str) -> Optional[dict]:
    access_token, app_base_url, test_mode = get_ziina_config()
    if not access_token:
        logging.error("Ziina access token missing.")
        return None
    amount_fils = int(round(amount_aed * 100))
    url = f"{ZIINA_API_BASE}/payment_intent"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    base_return = app_base_url.rstrip("/")
    success_url = f"{base_return}/payment_result?result=success&pi_id={{PAYMENT_INTENT_ID}}"
    cancel_url = f"{base_return}/payment_result?result=cancel&pi_id={{PAYMENT_INTENT_ID}}"
    failure_url = f"{base_return}/payment_result?result=failure&pi_id={{PAYMENT_INTENT_ID}}"
    payload = {
        "amount": amount_fils,
        "currency_code": "AED",
        "message": f"Snow Liwa booking {booking_id} - {customer_name}",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "failure_url": failure_url,
        "test": test_mode,
    }
    logging.info(f"[ZIINA] POST {url}")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
    except requests.RequestException as e:
        logging.error(f"Ziina request error: {e}")
        return None
    if resp.status_code not in (200, 201):
        logging.error(f"Ziina error status={resp.status_code} body={resp.text}")
        return None
    try:
        return resp.json()
    except Exception:
        return None


def get_payment_intent(pi_id: str) -> Optional[dict]:
    access_token, _, _ = get_ziina_config()
    if not access_token:
        return None
    url = f"{ZIINA_API_BASE}/payment_intent/{pi_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    logging.info(f"[ZIINA] GET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as e:
        logging.error(f"Ziina request error: {e}")
        return None
    if resp.status_code != 200:
        logging.error(f"Ziina error status={resp.status_code} body={resp.text}")
        return None
    try:
        return resp.json()
    except Exception:
        return None


def get_payment_intent_status(pi_id: str) -> Optional[str]:
    pi = get_payment_intent(pi_id)
    if not pi:
        return None
    return pi.get("status") or (pi.get("data") or {}).get("status")


def sync_all_bookings(df: pd.DataFrame) -> pd.DataFrame:
    """Update payment status for bookings with payment_intent_id."""
    if not has_ziina_configured():
        return df
    updated = False
    for idx, row in df.iterrows():
        pi_id = str(row.get("payment_intent_id") or "").strip()
        if not pi_id:
            continue
        status = get_payment_intent_status(pi_id)
        if not status:
            continue
        mask = df.index == idx
        if status == "completed":
            df.loc[mask, "status"] = "paid"
            df.loc[mask, "payment_status"] = status
            updated = True
        elif status in ("failed", "canceled"):
            df.loc[mask, "status"] = "cancelled"
            df.loc[mask, "payment_status"] = status
            updated = True
    if updated:
        save_bookings(df)
    return df
