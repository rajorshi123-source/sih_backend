from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Camera Schema
class CameraResponse(BaseModel):
    id: str
    position: str
    resolution: str
    fps: int
    status: str

    class Config:
        from_attributes = True

# Bus Schemas
class BusResponse(BaseModel):
    id: str
    bus_number: str
    registration_number: str
    route_id: Optional[str] = None
    route_name: Optional[str] = None
    route_code: Optional[str] = None
    current_lat: float
    current_lng: float
    speed_kmh: float
    heading: float
    status: str
    camera_status: str
    ai_status: str
    last_communication: datetime
    events_today_count: int
    cameras: Optional[List[CameraResponse]] = []

    class Config:
        from_attributes = True

class BusTelemetry(BaseModel):
    bus_id: str
    bus_number: str
    latitude: float
    longitude: float
    speed_kmh: float
    heading: float
    timestamp: datetime
    camera_status: str
    ai_status: str

# Route Schemas
class RouteResponse(BaseModel):
    id: str
    name: str
    route_code: str
    origin: str
    destination: str
    color: str
    waypoints_json: List[Any]
    distance_km: float
    avg_journey_mins: int
    status: str
    active_buses_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Road Defects & Clustering
class RoadDefectCreate(BaseModel):
    bus_id: str
    defect_type: str
    latitude: float
    longitude: float
    confidence: float
    severity: str
    evidence_image: Optional[str] = None

class RoadDefectClusterResponse(BaseModel):
    id: str
    cluster_code: str
    defect_type: str
    latitude: float
    longitude: float
    confidence: float
    severity: str
    status: str
    confirmed_buses_count: int
    total_detections: int
    first_detected_at: datetime
    last_detected_at: datetime
    address_description: Optional[str] = None
    evidence_image: Optional[str] = None

    class Config:
        from_attributes = True

# Traffic Schemas
class TrafficEventResponse(BaseModel):
    id: str
    bus_id: str
    route_id: Optional[str] = None
    location_name: str
    latitude: float
    longitude: float
    density_percent: int
    density_level: str
    avg_speed_kmh: float
    vehicle_count: int
    cars_count: int
    bikes_count: int
    buses_count: int
    trucks_count: int
    autos_count: int
    timestamp: datetime
    duration_minutes: int

    class Config:
        from_attributes = True

class TrafficSummary(BaseModel):
    overall_density_percent: int
    overall_density_level: str
    total_vehicles_active: int
    average_speed_kmh: float
    congestion_hotspots_count: int
    vehicle_breakdown: Dict[str, int]
    hourly_trend: List[Dict[str, Any]]

# Incidents Schemas
class IncidentResponse(BaseModel):
    id: str
    incident_code: str
    incident_type: str
    severity: str
    vehicle_track_id: Optional[str] = None
    detected_plate: Optional[str] = None
    corrected_plate: Optional[str] = None
    plate_confidence: float
    tracking_confidence: float
    bus_id: str
    route_id: Optional[str] = None
    latitude: float
    longitude: float
    location_name: str
    timestamp: datetime
    evidence_image: Optional[str] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class IncidentOCRCorrection(BaseModel):
    corrected_plate: str
    notes: Optional[str] = None

# Alert Schemas
class AlertResponse(BaseModel):
    id: str
    alert_code: str
    alert_type: str
    severity: str
    title: str
    message: str
    bus_id: Optional[str] = None
    route_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: datetime
    is_read: bool
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertAcknowledge(BaseModel):
    acknowledged_by: str

# Dashboard Summary Schema
class DashboardSummary(BaseModel):
    active_buses: int
    total_buses: int
    ai_events_today: int
    potholes_detected: int
    traffic_hotspots: int
    active_incidents: int
    waterlogging_points: int
    unresolved_defects: int
    recent_events: List[Dict[str, Any]]
    traffic_metrics: Dict[str, Any]
    road_health_metrics: Dict[str, Any]
    incident_summary: Dict[str, int]
    fleet_status: Dict[str, int]

# Video Analysis Schemas
class DetectionBox(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float] # [x, y, w, h] normalized 0-1
    track_id: Optional[int] = None
    speed_estimate_kmh: Optional[float] = None
    plate_text: Optional[str] = None

class VideoFrameResult(BaseModel):
    frame_number: int
    timestamp_sec: float
    detections: List[DetectionBox]
    vehicle_counts: Dict[str, int]
    density_percent: int
    safety_alerts: List[str]

class VideoAnalysisResponse(BaseModel):
    session_id: str
    video_name: str
    total_frames: int
    processed_frames: int
    fps: float
    duration_seconds: float
    events_generated: int
    frame_results: List[VideoFrameResult]
    summary_events: List[Dict[str, Any]]
    bus_id: str
    route_code: str

# Simulation Control Schemas
class SimulationState(BaseModel):
    is_running: bool
    speed_multiplier: float
    active_buses: int
    events_emitted_total: int
    last_update: datetime

class SimulationControl(BaseModel):
    action: str  # start, pause, set_speed, trigger_defect, trigger_incident
    speed_multiplier: Optional[float] = 1.0
    defect_type: Optional[str] = "POTHOLE"
    incident_type: Optional[str] = "HIT_AND_RUN"

# Settings Schemas
class SettingsResponse(BaseModel):
    ai_mode: str
    demo_mode: bool
    clustering_radius_meters: float
    pothole_confidence_threshold: float
    traffic_density_threshold: int
    license_plate_blurring: bool
    simulation_speed: float
    simulation_running: bool

class SettingsUpdate(BaseModel):
    clustering_radius_meters: Optional[float] = None
    pothole_confidence_threshold: Optional[float] = None
    traffic_density_threshold: Optional[int] = None
    license_plate_blurring: Optional[bool] = None
    simulation_speed: Optional[float] = None
    simulation_running: Optional[bool] = None
