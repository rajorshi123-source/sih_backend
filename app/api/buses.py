from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Bus, Camera, Route, Detection
from app.schemas.schemas import BusResponse, CameraResponse

router = APIRouter(prefix="/buses", tags=["Fleet Management"])

@router.get("", response_model=List[BusResponse])
def get_all_buses(
    status: Optional[str] = None,
    route_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Bus)
    if status:
        query = query.filter(Bus.status == status)
    if route_id:
        query = query.filter(Bus.route_id == route_id)

    buses = query.all()
    results = []
    for b in buses:
        results.append({
            "id": b.id,
            "bus_number": b.bus_number,
            "registration_number": b.registration_number,
            "route_id": b.route_id,
            "route_name": b.route.name if b.route else None,
            "route_code": b.route.route_code if b.route else None,
            "current_lat": b.current_lat,
            "current_lng": b.current_lng,
            "speed_kmh": b.speed_kmh,
            "heading": b.heading,
            "status": b.status,
            "camera_status": b.camera_status,
            "ai_status": b.ai_status,
            "last_communication": b.last_communication,
            "events_today_count": b.events_today_count,
            "cameras": b.cameras
        })
    return results

@router.get("/{bus_id}", response_model=BusResponse)
def get_bus_details(bus_id: str, db: Session = Depends(get_db)):
    # Query either by UUID or by bus_number e.g. BUS-024
    bus = db.query(Bus).filter((Bus.id == bus_id) | (Bus.bus_number == bus_id)).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    return {
        "id": bus.id,
        "bus_number": bus.bus_number,
        "registration_number": bus.registration_number,
        "route_id": bus.route_id,
        "route_name": bus.route.name if bus.route else None,
        "route_code": bus.route.route_code if bus.route else None,
        "current_lat": bus.current_lat,
        "current_lng": bus.current_lng,
        "speed_kmh": bus.speed_kmh,
        "heading": bus.heading,
        "status": bus.status,
        "camera_status": bus.camera_status,
        "ai_status": bus.ai_status,
        "last_communication": bus.last_communication,
        "events_today_count": bus.events_today_count,
        "cameras": bus.cameras
    }

@router.get("/{bus_id}/cameras", response_model=List[CameraResponse])
def get_bus_cameras(bus_id: str, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter((Bus.id == bus_id) | (Bus.bus_number == bus_id)).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus.cameras
