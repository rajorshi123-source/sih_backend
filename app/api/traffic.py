from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import TrafficEvent
from app.schemas.schemas import TrafficEventResponse, TrafficSummary
from app.services.traffic_service import TrafficService

router = APIRouter(prefix="/traffic", tags=["Traffic Intelligence"])

@router.get("/summary", response_model=TrafficSummary)
def get_traffic_summary(db: Session = Depends(get_db)):
    events = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).limit(20).all()
    total_vehicles = sum(e.vehicle_count for e in events) or 480
    avg_speed = sum(e.avg_speed_kmh for e in events) / len(events) if events else 22.5
    avg_density = sum(e.density_percent for e in events) // len(events) if events else 74

    hotspots_count = db.query(TrafficEvent).filter(TrafficEvent.density_level.in_(["HIGH", "SEVERE"])).count()
    distribution = TrafficService.calculate_vehicle_distribution(total_vehicles)

    hourly_trend = [
        {"hour": "06:00", "vehicles": 420, "speed": 42.5, "density": 35},
        {"hour": "07:00", "vehicles": 890, "speed": 34.0, "density": 58},
        {"hour": "08:00", "vehicles": 1450, "speed": 22.1, "density": 78},
        {"hour": "09:00", "vehicles": 1820, "speed": 16.4, "density": 88},
        {"hour": "10:00", "vehicles": 1650, "speed": 19.8, "density": 82},
        {"hour": "11:00", "vehicles": 1320, "speed": 25.0, "density": 65},
        {"hour": "12:00", "vehicles": 1180, "speed": 28.4, "density": 55},
        {"hour": "13:00", "vehicles": 1050, "speed": 31.2, "density": 48}
    ]

    return {
        "overall_density_percent": avg_density,
        "overall_density_level": "HIGH" if avg_density > 70 else "MEDIUM",
        "total_vehicles_active": total_vehicles,
        "average_speed_kmh": round(avg_speed, 1),
        "congestion_hotspots_count": hotspots_count,
        "vehicle_breakdown": distribution,
        "hourly_trend": hourly_trend
    }

@router.get("/events", response_model=List[TrafficEventResponse])
def get_traffic_events(db: Session = Depends(get_db)):
    return db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).all()

@router.get("/bottlenecks")
def get_traffic_bottlenecks(db: Session = Depends(get_db)):
    bottlenecks = db.query(TrafficEvent).filter(
        TrafficEvent.density_level.in_(["HIGH", "SEVERE"])
    ).order_by(TrafficEvent.density_percent.desc()).all()

    return [
        {
            "id": b.id,
            "location_name": b.location_name,
            "density_percent": b.density_percent,
            "density_level": b.density_level,
            "avg_speed_kmh": b.avg_speed_kmh,
            "vehicle_count": b.vehicle_count,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "bus_reporter": b.bus_id,
            "duration_minutes": b.duration_minutes
        }
        for b in bottlenecks
    ]
