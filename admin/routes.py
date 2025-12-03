"""Admin routes: dashboard, settings, sync payments."""
from __future__ import annotations
from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from core.config import ADMIN_PIN, PAGES_DIR
from services.payments_ziina import sync_all_bookings
from utils.io import load_bookings, save_bookings
from utils.settings_utils import load_settings, save_settings
import secrets

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=str(PAGES_DIR))
security = HTTPBasic()


def verify_pin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin PIN using HTTP Basic Auth (username=admin, password=PIN)."""
    correct_pin = secrets.compare_digest(credentials.password, ADMIN_PIN)
    if not correct_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, credentials: HTTPBasicCredentials = Depends(verify_pin)):
    """Admin dashboard: show bookings and KPIs."""
    df = load_bookings()
    
    total_bookings = len(df)
    total_tickets = int(df["tickets"].sum()) if not df.empty else 0
    total_amount = float(df["total_amount"].sum()) if not df.empty else 0.0
    total_paid = float(df[df["status"] == "paid"]["total_amount"].sum()) if not df.empty else 0.0
    total_pending = float(df[df["status"] == "pending"]["total_amount"].sum()) if not df.empty else 0.0
    
    bookings = df.sort_values("created_at", ascending=False).head(25).to_dict("records") if not df.empty else []
    
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "total_bookings": total_bookings,
            "total_tickets": total_tickets,
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "bookings": bookings,
        },
    )


@router.post("/sync")
async def sync_payments(credentials: HTTPBasicCredentials = Depends(verify_pin)):
    """Sync payment status with Ziina."""
    df = load_bookings()
    df = sync_all_bookings(df)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, credentials: HTTPBasicCredentials = Depends(verify_pin)):
    """Admin settings page."""
    settings = load_settings()
    return templates.TemplateResponse("admin_settings.html", {"request": request, "settings": settings})


@router.post("/settings")
async def save_settings_route(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(verify_pin),
):
    """Save admin settings."""
    form_data = await request.form()
    settings = load_settings()
    
    # Update settings from form
    for key in form_data:
        settings[key] = form_data[key]
    
    save_settings(settings)
    return RedirectResponse(url="/admin/settings?saved=true", status_code=303)
