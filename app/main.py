import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.api import (
    auth, dashboard, buses, routes, defects, traffic,
    incidents, alerts, video, analytics, reports, settings as sys_settings, simulation
)
from app.websocket.connection_manager import ws_manager
from app.services.simulation_engine import simulation_engine
from app.services.evidence_service import EvidenceService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables, stock evidence, and start simulation loop
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("[Startup warning - db tables]:", e)

    try:
        EvidenceService.create_stock_evidence()
    except Exception as e:
        print("[Startup warning - stock evidence]:", e)

    if not os.getenv("VERCEL"):
        try:
            simulation_engine.start()
            print("[BusSense AI] Backend initialized. Simulation engine running.")
        except Exception as e:
            print("[Startup warning - simulation engine]:", e)
    else:
        print("[BusSense AI] Backend initialized in Vercel Serverless mode.")

    yield

    # Shutdown
    if not os.getenv("VERCEL"):
        try:
            simulation_engine.pause()
            print("[BusSense AI] Shutting down simulation engine.")
        except Exception:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files for Evidence Images
app.mount("/evidence", StaticFiles(directory=settings.EVIDENCE_DIR), name="evidence")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(buses.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(defects.router, prefix=settings.API_V1_PREFIX)
app.include_router(traffic.router, prefix=settings.API_V1_PREFIX)
app.include_router(incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(video.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(sys_settings.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulation.router, prefix=settings.API_V1_PREFIX)

# WebSocket Endpoints
@app.websocket("/ws/fleet")
async def websocket_fleet_endpoint(websocket: WebSocket):
    await ws_manager.connect_fleet(websocket)
    try:
        while True:
            # Keep-alive receive ping
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_fleet(websocket)

@app.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await ws_manager.connect_events(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_events(websocket)

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect_alerts(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_alerts(websocket)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "demo_mode": settings.DEMO_MODE,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
