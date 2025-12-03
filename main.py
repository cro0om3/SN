"""Snow Liwa FastAPI app - main entry point."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import ASSETS_DIR
from app.routes import router as app_router
from admin.routes import router as admin_router

app = FastAPI(title="Snow Liwa", version="1.0.0")

# Mount static assets
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Include routers
app.include_router(app_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
