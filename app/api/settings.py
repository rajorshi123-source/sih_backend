from fastapi import APIRouter
from app.config import settings
from app.schemas.schemas import SettingsResponse, SettingsUpdate
from app.services.simulation_engine import simulation_engine

router = APIRouter(prefix="/settings", tags=["System Settings"])

# In-memory mutable configuration store
system_settings = {
    "clustering_radius_meters": 35.0,
    "pothole_confidence_threshold": 0.85,
    "traffic_density_threshold": 75,
    "license_plate_blurring": True,
}

@router.get("", response_model=SettingsResponse)
def get_system_settings():
    return {
        "ai_mode": settings.AI_MODE,
        "demo_mode": settings.DEMO_MODE,
        "clustering_radius_meters": system_settings["clustering_radius_meters"],
        "pothole_confidence_threshold": system_settings["pothole_confidence_threshold"],
        "traffic_density_threshold": system_settings["traffic_density_threshold"],
        "license_plate_blurring": system_settings["license_plate_blurring"],
        "simulation_speed": simulation_engine.speed_multiplier,
        "simulation_running": simulation_engine.is_running
    }

@router.patch("", response_model=SettingsResponse)
def update_system_settings(payload: SettingsUpdate):
    if payload.clustering_radius_meters is not None:
        system_settings["clustering_radius_meters"] = payload.clustering_radius_meters
    if payload.pothole_confidence_threshold is not None:
        system_settings["pothole_confidence_threshold"] = payload.pothole_confidence_threshold
    if payload.traffic_density_threshold is not None:
        system_settings["traffic_density_threshold"] = payload.traffic_density_threshold
    if payload.license_plate_blurring is not None:
        system_settings["license_plate_blurring"] = payload.license_plate_blurring
    if payload.simulation_speed is not None:
        simulation_engine.set_speed(payload.simulation_speed)
    if payload.simulation_running is not None:
        if payload.simulation_running:
            simulation_engine.start()
        else:
            simulation_engine.pause()

    return get_system_settings()
