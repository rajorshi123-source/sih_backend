import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Analyst", nullable=False)  # Administrator, Transport Authority, Traffic Officer, Maintenance Officer, Analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Route(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    route_code = Column(String(20), unique=True, nullable=False, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    color = Column(String(20), default="#3b82f6")
    waypoints_json = Column(JSON, nullable=False)  # List of [lat, lng, name]
    distance_km = Column(Float, default=12.5)
    avg_journey_mins = Column(Integer, default=45)
    status = Column(String(20), default="ACTIVE")
    buses = relationship("Bus", back_populates="route")

class Bus(Base):
    __tablename__ = "buses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bus_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., BUS-024
    registration_number = Column(String(30), nullable=False)                 # e.g., WB-04-E-1024
    route_id = Column(String(36), ForeignKey("routes.id"), nullable=True)
    current_lat = Column(Float, nullable=False)
    current_lng = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=28.0)
    heading = Column(Float, default=90.0)
    status = Column(String(20), default="ACTIVE")                            # ACTIVE, INACTIVE, MAINTENANCE
    camera_status = Column(String(20), default="ONLINE")                     # ONLINE, DEGRADED, OFFLINE
    ai_status = Column(String(20), default="ONLINE")                         # ONLINE, DEGRADED, OFFLINE
    last_communication = Column(DateTime, default=datetime.utcnow)
    events_today_count = Column(Integer, default=0)
    current_waypoint_index = Column(Integer, default=0)
    direction_forward = Column(Boolean, default=True)

    route = relationship("Route", back_populates="buses")
    cameras = relationship("Camera", back_populates="bus")

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bus_id = Column(String(36), ForeignKey("buses.id"), nullable=False)
    position = Column(String(20), nullable=False)  # FRONT, REAR, LEFT, RIGHT, CABIN
    resolution = Column(String(20), default="1080p")
    fps = Column(Integer, default=30)
    status = Column(String(20), default="ONLINE")

    bus = relationship("Bus", back_populates="cameras")

class BusLocation(Base):
    __tablename__ = "bus_locations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bus_id = Column(String(36), ForeignKey("buses.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=0.0)
    heading = Column(Float, default=0.0)

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bus_id = Column(String(36), nullable=False, index=True)
    route_id = Column(String(36), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # car, bus, pothole, waterlogging, etc.
    confidence = Column(Float, nullable=False)
    bbox_json = Column(JSON, nullable=True)                    # [x, y, w, h] or normalized
    frame_number = Column(Integer, default=0)
    evidence_path = Column(String(255), nullable=True)

class RoadDefectCluster(Base):
    __tablename__ = "road_defect_clusters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_code = Column(String(30), unique=True, nullable=False, index=True) # e.g. RD-1024
    defect_type = Column(String(50), nullable=False, index=True)               # POTHOLE, DAMAGED_ROAD, CRACK, WATERLOGGING, MISSING_DIVIDER, MISSING_ZEBRA, DAMAGED_SIGN
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    confidence = Column(Float, default=0.92)
    severity = Column(String(20), default="HIGH", index=True)                  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="UNRESOLVED", index=True)             # UNRESOLVED, UNDER_REVIEW, WORK_ORDER_ISSUED, REPAIRED, REJECTED
    confirmed_buses_count = Column(Integer, default=1)
    total_detections = Column(Integer, default=1)
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    last_detected_at = Column(DateTime, default=datetime.utcnow)
    address_description = Column(String(255), nullable=True)
    evidence_image = Column(String(255), nullable=True)

    defects = relationship("RoadDefect", back_populates="cluster")

class RoadDefect(Base):
    __tablename__ = "road_defects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_id = Column(String(36), ForeignKey("road_defect_clusters.id"), nullable=True, index=True)
    bus_id = Column(String(36), nullable=False)
    defect_type = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    confidence = Column(Float, default=0.90)
    severity = Column(String(20), default="HIGH")
    detected_at = Column(DateTime, default=datetime.utcnow)
    evidence_image = Column(String(255), nullable=True)

    cluster = relationship("RoadDefectCluster", back_populates="defects")

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bus_id = Column(String(36), nullable=False)
    route_id = Column(String(36), nullable=True)
    location_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    density_percent = Column(Integer, default=50)
    density_level = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, SEVERE
    avg_speed_kmh = Column(Float, default=22.0)
    vehicle_count = Column(Integer, default=30)
    cars_count = Column(Integer, default=15)
    bikes_count = Column(Integer, default=8)
    buses_count = Column(Integer, default=3)
    trucks_count = Column(Integer, default=2)
    autos_count = Column(Integer, default=2)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, default=15)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_code = Column(String(30), unique=True, nullable=False, index=True) # e.g. INC-2026-0012
    incident_type = Column(String(50), nullable=False, index=True)              # HIT_AND_RUN, RASH_DRIVING, PEDESTRIAN_SAFETY_RISK, ROAD_HAZARD
    severity = Column(String(20), default="HIGH", index=True)                   # CRITICAL, HIGH, MEDIUM, LOW
    vehicle_track_id = Column(String(50), nullable=True)
    detected_plate = Column(String(30), nullable=True)
    corrected_plate = Column(String(30), nullable=True)
    plate_confidence = Column(Float, default=0.88)
    tracking_confidence = Column(Float, default=0.90)
    bus_id = Column(String(36), nullable=False)
    route_id = Column(String(36), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    evidence_image = Column(String(255), nullable=True)
    status = Column(String(30), default="NEW", index=True)                      # NEW, UNDER_REVIEW, VERIFIED, RESOLVED, FALSE_POSITIVE
    notes = Column(Text, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_code = Column(String(30), unique=True, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True) # POTHOLE_CRITICAL, WATERLOGGING_SEVERE, HIT_AND_RUN, RASH_DRIVING, PEDESTRIAN_RISK, CONGESTION_SEVERE
    severity = Column(String(20), default="HIGH", index=True)   # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    bus_id = Column(String(36), nullable=True)
    route_id = Column(String(36), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_type = Column(String(50), nullable=False) # ROAD_HEALTH, TRAFFIC, FLEET, INCIDENTS, ROUTE_PERFORMANCE
    title = Column(String(150), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    generated_by = Column(String(100), default="System Administrator")
    status = Column(String(20), default="COMPLETED")
    summary_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    username = Column(String(50), default="system")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=True)
    details_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
