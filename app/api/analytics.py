from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Bus, RoadDefectCluster, TrafficEvent, Incident

router = APIRouter(prefix="/analytics", tags=["Urban Analytics"])

@router.get("/traffic")
def get_traffic_analytics(db: Session = Depends(get_db)):
    return {
        "hourly_volume": [
            {"time": "05:00", "vehicles": 210, "avg_speed": 45.0, "congestion_pct": 20},
            {"time": "07:00", "vehicles": 680, "avg_speed": 36.5, "congestion_pct": 45},
            {"time": "09:00", "vehicles": 1820, "avg_speed": 16.4, "congestion_pct": 88},
            {"time": "11:00", "vehicles": 1320, "avg_speed": 24.0, "congestion_pct": 62},
            {"time": "13:00", "vehicles": 1050, "avg_speed": 30.2, "congestion_pct": 48},
            {"time": "15:00", "vehicles": 1280, "avg_speed": 26.5, "congestion_pct": 58},
            {"time": "17:00", "vehicles": 1940, "avg_speed": 14.8, "congestion_pct": 92},
            {"time": "19:00", "vehicles": 1710, "avg_speed": 18.2, "congestion_pct": 84},
            {"time": "21:00", "vehicles": 920, "avg_speed": 34.0, "congestion_pct": 38}
        ],
        "vehicle_type_distribution": [
            {"name": "Cars", "value": 45, "color": "#3b82f6"},
            {"name": "Motorcycles", "value": 28, "color": "#10b981"},
            {"name": "Auto Rickshaws", "value": 14, "color": "#f59e0b"},
            {"name": "Public Buses", "value": 8, "color": "#8b5cf6"},
            {"name": "Commercial Trucks", "value": 5, "color": "#ef4444"}
        ],
        "top_bottlenecks": [
            {"corridor": "Chingrighata EM Bypass", "delay_mins": 24, "speed": 8.5},
            {"corridor": "Howrah Bridge Approach", "delay_mins": 19, "speed": 11.2},
            {"corridor": "Park Circus 7-Point", "delay_mins": 16, "speed": 14.5},
            {"corridor": "Shyambazar 5-Point", "delay_mins": 12, "speed": 16.0}
        ]
    }

@router.get("/road-health")
def get_road_health_analytics(db: Session = Depends(get_db)):
    clusters = db.query(RoadDefectCluster).all()
    defect_counts = {}
    severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    status_counts = {"UNRESOLVED": 0, "UNDER_REVIEW": 0, "WORK_ORDER_ISSUED": 0, "REPAIRED": 0}

    for c in clusters:
        dtype = c.defect_type.replace("_", " ")
        defect_counts[dtype] = defect_counts.get(dtype, 0) + 1
        if c.severity in severity_counts:
            severity_counts[c.severity] += 1
        if c.status in status_counts:
            status_counts[c.status] += 1

    return {
        "defect_type_breakdown": [{"type": k, "count": v} for k, v in defect_counts.items()],
        "severity_distribution": [{"severity": k, "count": v} for k, v in severity_counts.items()],
        "repair_pipeline_status": [{"status": k, "count": v} for k, v in status_counts.items()],
        "defect_discovery_rate_per_day": [
            {"day": "Mon", "new_defects": 24, "repaired": 8},
            {"day": "Tue", "new_defects": 19, "repaired": 12},
            {"day": "Wed", "new_defects": 31, "repaired": 15},
            {"day": "Thu", "new_defects": 22, "repaired": 14},
            {"day": "Fri", "new_defects": 28, "repaired": 11},
            {"day": "Sat", "new_defects": 14, "repaired": 18},
            {"day": "Sun", "new_defects": 9, "repaired": 6}
        ]
    }

@router.get("/fleet")
def get_fleet_analytics(db: Session = Depends(get_db)):
    return {
        "active_bus_ratio": 85.0,
        "camera_uptime_percentage": 98.4,
        "edge_ai_uptime_percentage": 99.1,
        "avg_daily_km_per_bus": 142.5,
        "total_urban_distance_covered_km": 2850,
        "fleet_age_distribution": [
            {"category": "< 2 Years", "count": 8},
            {"category": "2 - 5 Years", "count": 9},
            {"category": "> 5 Years", "count": 3}
        ]
    }

@router.get("/ai-performance")
def get_ai_performance():
    return {
        "model_accuracy": 94.6,
        "average_inference_time_ms": 28.4,
        "false_positive_rate": 2.8,
        "daily_inferences": 284000,
        "events_flagged_for_transmission": 1284,
        "bandwidth_saved_percentage": 99.4,
        "confidence_brackets": [
            {"bracket": "95 - 100%", "events": 842},
            {"bracket": "90 - 94%", "events": 315},
            {"bracket": "85 - 89%", "events": 98},
            {"bracket": "< 85%", "events": 29}
        ]
    }
