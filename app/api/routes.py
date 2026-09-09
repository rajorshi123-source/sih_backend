from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Route, Bus, RoadDefectCluster, TrafficEvent
from app.schemas.schemas import RouteResponse

router = APIRouter(prefix="/routes", tags=["Routes & Network"])

@router.get("", response_model=List[RouteResponse])
def get_all_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    results = []
    for r in routes:
        active_buses = db.query(Bus).filter(Bus.route_id == r.id, Bus.status == "ACTIVE").count()
        results.append({
            "id": r.id,
            "name": r.name,
            "route_code": r.route_code,
            "origin": r.origin,
            "destination": r.destination,
            "color": r.color,
            "waypoints_json": r.waypoints_json,
            "distance_km": r.distance_km,
            "avg_journey_mins": r.avg_journey_mins,
            "status": r.status,
            "active_buses_count": active_buses
        })
    return results

@router.get("/analytics/ranking")
def get_routes_ranking(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    rankings = []
    for r in routes:
        # Calculate simulated congestion score and delay
        congestion_level = "HIGH" if r.route_code in ["R-101", "R-102", "R-105"] else ("MEDIUM" if r.route_code in ["R-103", "R-106"] else "LOW")
        avg_delay_mins = 18 if congestion_level == "HIGH" else (9 if congestion_level == "MEDIUM" else 3)
        rankings.append({
            "route_id": r.id,
            "route_code": r.route_code,
            "name": r.name,
            "congestion_level": congestion_level,
            "avg_speed_kmh": 16.4 if congestion_level == "HIGH" else 28.5,
            "avg_delay_mins": avg_delay_mins,
            "defects_count": 5 if congestion_level == "HIGH" else 2,
            "traffic_hotspots_count": 3 if congestion_level == "HIGH" else 1,
            "efficiency_score": 68 if congestion_level == "HIGH" else 89
        })
    rankings.sort(key=lambda x: x["avg_delay_mins"], reverse=True)
    return rankings

@router.get("/od-matrix")
def get_origin_destination_matrix():
    """Origin-Destination passenger flow matrix (Simulated Demo Data)."""
    hubs = ["Howrah", "Esplanade", "Salt Lake", "Park Street", "Garia", "Dum Dum", "Sealdah"]
    matrix = [
        {"origin": "Howrah", "destination": "Esplanade", "flow": 14200, "status": "HEAVY"},
        {"origin": "Salt Lake", "destination": "Park Street", "flow": 9800, "status": "HEAVY"},
        {"origin": "Garia", "destination": "Esplanade", "flow": 8600, "status": "MODERATE"},
        {"origin": "Dum Dum", "destination": "Howrah", "flow": 11500, "status": "HEAVY"},
        {"origin": "Sealdah", "destination": "Salt Lake", "flow": 7900, "status": "MODERATE"},
        {"origin": "Howrah", "destination": "Park Street", "flow": 6400, "status": "MODERATE"},
        {"origin": "Esplanade", "destination": "Garia", "flow": 8200, "status": "MODERATE"},
        {"origin": "Dum Dum", "destination": "Sealdah", "flow": 9100, "status": "HEAVY"}
    ]
    return {
        "is_demo_data": True,
        "hubs": hubs,
        "flows": matrix,
        "peak_hour": "08:30 AM - 10:30 AM",
        "total_trips_simulated": 75700
    }
