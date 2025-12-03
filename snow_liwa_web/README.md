# SNOW LIWA Web – FastAPI Edition

**Modern, Fast, Production-ready booking system with Ziina payment integration**

This is a complete rewrite of the Snow Liwa booking app using **FastAPI** instead of Streamlit, with:

- ✅ **Clear structure**: `app/`, `admin/`, `core/`, `services/`, `utils/`, `pages/`, `assets/`
- ✅ **Same business logic**: booking creation, Ziina payment intents, payment status sync
- ✅ **Beautiful landing page**: Uses `Snn/FHD/1.html` design
- ✅ **Admin dashboard**: KPIs, booking list, payment sync, settings
- ✅ **HTTP Basic Auth** for admin routes (PIN-based)
- ✅ **Environment-based config**: `.env` file for secrets

---

## 📁 Project Structure

```
snow_liwa_web/
├── main.py                      # FastAPI app entry point
├── app/
│   ├── __init__.py
│   └── routes.py                # Public routes: /, /book, /payment_result
├── admin/
│   ├── __init__.py
│   └── routes.py                # Admin routes: /admin/dashboard, /admin/settings, /admin/sync
├── core/
│   └── config.py                # Environment config, constants, Ziina secrets
├── services/
│   └── payments_ziina.py        # Payment integration (create/get intents, sync)
├── utils/
│   ├── io.py                    # Bookings Excel I/O
│   ├── logic.py                 # Booking ID generation, creation
│   └── settings_utils.py        # Settings JSON persistence
├── pages/                       # Jinja2 templates
│   ├── payment_result.html
│   ├── admin_dashboard.html
│   └── admin_settings.html
├── assets/                      # Static files (CSS)
│   └── admin.css
├── data/                        # Auto-generated on first run
│   ├── bookings.xlsx
│   └── settings.json
├── requirements.txt
├── .env.example                 # Copy to .env and fill in
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd snow_liwa_web
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```env
# Ziina Payment Configuration
ZIINA_ACCESS_TOKEN=your_ziina_access_token_here
ZIINA_APP_BASE_URL=http://localhost:8000
ZIINA_TEST_MODE=true

# Admin PIN (HTTP Basic Auth password, username is "admin")
ADMIN_PIN=change_me

# Business Settings
TICKET_PRICE_AED=175
```

### 3. Run the App

```powershell
python main.py
```

Or with uvicorn directly:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The app will be available at:

- **Public site**: <http://localhost:8000>
- **Admin dashboard**: <http://localhost:8000/admin/dashboard> (requires PIN)
- **Health check**: <http://localhost:8000/health>

---

## 🔑 Admin Access

Admin routes are protected with **HTTP Basic Authentication**:

- **Username**: `admin`
- **Password**: value of `ADMIN_PIN` from `.env`

Your browser will prompt you for credentials when accessing `/admin/*` routes.

---

## 📋 Features

### Public Routes

| Route              | Method | Description                                      |
|--------------------|--------|--------------------------------------------------|
| `/`                | GET    | Landing page (uses `Snn/FHD/1.html`)             |
| `/book`            | POST   | Submit booking form, create payment, redirect    |
| `/payment_result`  | GET    | Handle Ziina redirect (success/cancel/failure)   |

### Admin Routes

| Route               | Method | Description                              |
|---------------------|--------|------------------------------------------|
| `/admin/dashboard`  | GET    | View KPIs and last 25 bookings           |
| `/admin/sync`       | POST   | Sync payment status from Ziina           |
| `/admin/settings`   | GET    | View/edit app settings                   |
| `/admin/settings`   | POST   | Save settings                            |

---

## 🧪 Testing Locally

1. **Test public booking**:
   - Visit <http://localhost:8000>
   - Fill in the booking form
   - Submit → redirects to Ziina (or shows error if not configured)

2. **Test admin**:
   - Visit <http://localhost:8000/admin/dashboard>
   - Enter username `admin` and your PIN
   - View bookings, sync payments, adjust settings

3. **Test payment result**:
   - Manually visit: <http://localhost:8000/payment_result?result=success&pi_id=test123>
   - Should display success/failure/pending message

---

## 🌐 Deployment

### Ziina Production Mode

1. Set `ZIINA_TEST_MODE=false` in `.env`
2. Use your production Ziina access token
3. Set `ZIINA_APP_BASE_URL` to your public domain (e.g., `https://snowliwa.com`)

### Hosting Options

#### Option 1: Traditional VPS/VM

```powershell
# Install Python 3.10+
# Clone repo
git clone <repo-url>
cd snow_liwa_web

# Setup virtual env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with production values

# Run with uvicorn (production mode)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Set up **Nginx** or **IIS** as reverse proxy for HTTPS.

#### Option 2: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```powershell
docker build -t snow-liwa-web .
docker run -d -p 8000:8000 --env-file .env snow-liwa-web
```

#### Option 3: Platform-as-a-Service (PaaS)

**Render / Railway / Fly.io**:

1. Push code to GitHub
2. Connect repo to platform
3. Set environment variables in platform UI
4. Deploy

---

## 🛠️ Development Tips

### Hot Reload

```powershell
uvicorn main:app --reload
```

Any changes to `.py` files will auto-reload the server.

### Debugging

Add breakpoints in VS Code or use:

```python
import pdb; pdb.set_trace()
```

### Logs

FastAPI logs appear in console. Adjust log level in `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Data Files

- **Bookings**: `data/bookings.xlsx` – Excel file with all booking records
- **Settings**: `data/settings.json` – App settings (editable via admin panel)

Both are auto-created on first run if missing.

---

## 🔒 Security Notes

1. **Admin PIN**: Change default PIN in `.env` before deployment
2. **HTTPS**: Always use HTTPS in production (reverse proxy with SSL cert)
3. **Ziina Secrets**: Never commit `.env` to version control (already in `.gitignore`)
4. **CORS**: If needed, add CORS middleware in `main.py`

---

## 🆘 Troubleshooting

### Issue: "Ziina access token missing"

→ Check `.env` file exists and `ZIINA_ACCESS_TOKEN` is set.

### Issue: "401 Unauthorized" on admin routes

→ Enter username `admin` and correct PIN from `.env`.

### Issue: Payment redirect not working

→ Ensure `ZIINA_APP_BASE_URL` matches your public URL (must be accessible by Ziina servers).

### Issue: Excel file errors

→ Delete `data/bookings.xlsx` and restart app (auto-recreates).

---

## 🎨 Customization

### Update Landing Page

Edit `Snn/FHD/1.html` or create custom Jinja2 template in `pages/landing.html`.

### Update Admin Dashboard

Edit `pages/admin_dashboard.html` and `assets/admin.css`.

### Add New Routes

1. Add route handler in `app/routes.py` or `admin/routes.py`
2. Create Jinja2 template in `pages/`
3. Restart server

---

## 📝 License

Proprietary – SNOW LIWA Project.

---

## 📧 Contact

For support or questions, contact the SNOW LIWA team via WhatsApp/Instagram: **snowliwa**

---

**Enjoy your modern, production-ready booking system! ❄️🚀**
