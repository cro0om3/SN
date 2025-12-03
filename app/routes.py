"""Public-facing routes: landing, booking, payment result."""
from __future__ import annotations
import logging
import urllib.parse
from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config import TICKET_PRICE_AED, PAGES_DIR
from services.payments_ziina import has_ziina_configured, create_payment_intent, get_payment_intent
from utils.logic import create_booking_and_get_amount
from utils.io import load_bookings, save_bookings

router = APIRouter()
templates = Jinja2Templates(directory=str(PAGES_DIR))

logging.basicConfig(level=logging.INFO)

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Serve the landing page (1.html)."""
    landing_html = Path(__file__).resolve().parent.parent.parent / "FHD" / "1.html"
    if landing_html.exists():
        content = landing_html.read_text(encoding="utf-8")
        # Replace booking form action to point to /book
        content = content.replace('action="#"', 'action="/book"')
        content = content.replace('onsubmit="return false;"', '')
        return HTMLResponse(content=content)
    else:
        return templates.TemplateResponse("landing.html", {"request": request, "ticket_price": TICKET_PRICE_AED})


@router.post("/book")
async def book_ticket(
    name: str = Form(...),
    phone: str = Form(...),
    tickets: int = Form(...),
    notes: str = Form(""),
):
    """Create booking and redirect to Ziina payment."""
    if not name.strip() or not phone.strip():
        raise HTTPException(status_code=400, detail="Name and phone required.")
    
    form_data = {"name": name, "phone": phone, "tickets": int(tickets), "notes": notes}
    booking_id, total_amount = create_booking_and_get_amount(form_data)
    
    if not has_ziina_configured():
        logging.warning("Ziina not configured; booking saved as pending.")
        return HTMLResponse(
            f"<h1>Booking Created</h1><p>Booking ID: {booking_id}</p>"
            f"<p>Total: {total_amount:.2f} AED</p>"
            "<p>Ziina payment not configured. Contact admin to complete payment.</p>"
        )
    
    pi = create_payment_intent(total_amount, booking_id, name)
    if not pi:
        raise HTTPException(status_code=500, detail="Failed to create payment intent.")
    
    payment_intent_id = str(
        pi.get("id")
        or pi.get("payment_intent_id")
        or (pi.get("paymentIntent", {}) or {}).get("id")
        or ""
    )
    redirect_url = (
        pi.get("redirect_url")
        or pi.get("hosted_page_url")
        or (pi.get("next_action") or {}).get("redirect_url")
    )
    
    def _find_first_url(obj):
        if isinstance(obj, str) and (obj.startswith("http://") or obj.startswith("https://")):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                found = _find_first_url(v)
                if found:
                    return found
        if isinstance(obj, list):
            for item in obj:
                found = _find_first_url(item)
                if found:
                    return found
        return None
    
    if not redirect_url:
        redirect_url = _find_first_url(pi)
    
    # Update booking with payment_intent_id
    df = load_bookings()
    mask = df["booking_id"].astype(str) == str(booking_id)
    if mask.any():
        df.loc[mask, "payment_intent_id"] = payment_intent_id or ""
        df.loc[mask, "payment_status"] = pi.get("status") or df.loc[mask, "payment_status"]
        df.loc[mask, "redirect_url"] = redirect_url
        if pi.get("status") == "completed":
            df.loc[mask, "status"] = "paid"
        save_bookings(df)
    
    if redirect_url:
        return RedirectResponse(url=redirect_url, status_code=303)
    else:
        raise HTTPException(status_code=500, detail="Payment intent created but no redirect URL.")


@router.get("/payment_result", response_class=HTMLResponse)
async def payment_result(request: Request, result: str = "", pi_id: str = ""):
    """Handle Ziina redirect after payment (success/cancel/failure)."""
    raw_pi = pi_id.strip()
    pi_id_norm = urllib.parse.unquote(raw_pi).strip().strip('{}\"')
    
    df = load_bookings()
    row = df[df["payment_intent_id"].astype(str) == pi_id_norm]
    if row.empty and pi_id_norm:
        row = df[df["payment_intent_id"].astype(str).str.contains(pi_id_norm, na=False)]
    
    booking_id = row["booking_id"].iloc[0] if not row.empty else None
    booking_data = row.to_dict('records')[0] if not row.empty else None
    
    pi_status = None
    if pi_id_norm:
        pi = get_payment_intent(pi_id_norm)
        if pi:
            pi_status = pi.get("status") or (pi.get("data") or {}).get("status")
            returned_id = pi.get("id") or (pi.get("data") or {}).get("id") or pi.get("payment_intent_id")
            if returned_id:
                returned_id = str(returned_id)
                if returned_id != pi_id_norm:
                    pi_id_norm = returned_id
            
            if not row.empty:
                mask = df.index == row.index[0]
                if pi_status:
                    df.loc[mask, "payment_status"] = pi_status
                    if pi_status == "completed":
                        df.loc[mask, "status"] = "paid"
                    elif pi_status in ("failed", "canceled"):
                        df.loc[mask, "status"] = "cancelled"
                    save_bookings(df)
    
    final_status = pi_status or result
    
    return templates.TemplateResponse(
        "payment_result.html",
        {
            "request": request,
            "booking_id": booking_id,
            "booking_data": booking_data,
            "pi_id": pi_id_norm,
            "status": final_status,
        },
    )


@router.get("/ticket/{booking_id}", response_class=HTMLResponse)
async def download_ticket(booking_id: str):
    """Generate and return ticket HTML for a booking."""
    from utils.ticket_generator import generate_ticket_html
    
    df = load_bookings()
    row = df[df["booking_id"] == booking_id]
    
    if row.empty:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking_data = row.to_dict('records')[0]
    
    # Only generate ticket for paid bookings
    if booking_data.get("status") != "paid":
        raise HTTPException(status_code=403, detail="Ticket only available for paid bookings")
    
    ticket_html = generate_ticket_html(booking_data)
    return HTMLResponse(content=ticket_html)
