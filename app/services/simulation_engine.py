import asyncio
import random
import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.models.models import Bus, Route, BusLocation, Detection, TrafficEvent, Incident, Alert
from app.services.clustering_service import DefectClusteringService
from app.services.traffic_service import TrafficService
from app.websocket.connection_manager import ws_manager

class SimulationEngine:
    def __init__(self):
        self.is_running = True
        self.speed_multiplier = 1.0
        self.task: Optional[asyncio.Task] = None
        self.step_counter = 0

    def start(self):
        self.is_running = True
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())

    def pause(self):
        self.is_running = False

    def set_speed(self, multiplier: float):
        self.speed_multiplier = max(0.2, min(10.0, multiplier))

    async def run_loop(self):
        while True:
            if not self.is_running:
                await asyncio.sleep(1.0)
                continue

            try:
                await self.tick()
            except Exception as e:
                print(f"[SimulationEngine Error] {e}")

            # Base tick every 2 seconds / speed_multiplier
            sleep_time = max(0.2, 2.0 / self.speed_multiplier)
            await asyncio.sleep(sleep_time)

    async def tick(self):
        self.step_counter += 1
        db: Session = SessionLocal()
        try:
            buses = db.query(Bus).filter(Bus.status == "ACTIVE").all()
            if not buses:
                return

            updated_fleet = []

            for bus in buses:
                route = bus.route
                if not route or not route.waypoints_json:
                    continue

                waypoints = route.waypoints_json
                num_wp = len(waypoints)
                if num_wp < 2:
                    continue

                idx = bus.current_waypoint_index or 0
                forward = bus.direction_forward

                # Move to next waypoint or reverse at terminal
                if forward:
                    next_idx = idx + 1
                    if next_idx >= num_wp:
                        next_idx = num_wp - 2
                        bus.direction_forward = False
                else:
                    next_idx = idx - 1
                    if next_idx < 0:
                        next_idx = 1
                        bus.direction_forward = True

                bus.current_waypoint_index = next_idx
                wp = waypoints[next_idx]
                target_lat, target_lng = wp[0], wp[1]

                # Add tiny natural jitter (+- 0.0001)
                bus.current_lat = target_lat + random.uniform(-0.0001, 0.0001)
                bus.current_lng = target_lng + random.uniform(-0.0001, 0.0001)

                # Realistic speed based on location
                base_speed = 30.0
                if random.random() < 0.2:
                    base_speed = random.uniform(10.0, 18.0) # congestion
                else:
                    base_speed = random.uniform(25.0, 42.0)

                bus.speed_kmh = round(base_speed, 1)
                bus.last_communication = datetime.utcnow()

                # Calculate heading
                prev_wp = waypoints[idx]
                dlat = target_lat - prev_wp[0]
                dlng = target_lng - prev_wp[1]
                heading = (math.degrees(math.atan2(dlng, dlat)) + 360) % 360
                bus.heading = round(heading, 1)

                updated_fleet.append({
                    "id": bus.id,
                    "bus_number": bus.bus_number,
                    "registration_number": bus.registration_number,
                    "route_code": route.route_code,
                    "route_name": route.name,
                    "lat": bus.current_lat,
                    "lng": bus.current_lng,
                    "speed": bus.speed_kmh,
                    "heading": bus.heading,
                    "status": bus.status,
                    "camera_status": bus.camera_status,
                    "ai_status": bus.ai_status,
                    "events_today": bus.events_today_count
                })

            db.commit()

            # Broadcast fleet positions over WebSocket
            await ws_manager.broadcast_fleet({
                "type": "FLEET_UPDATE",
                "timestamp": datetime.utcnow().isoformat(),
                "buses": updated_fleet
            })

            # Every 3 steps, simulate an AI detection event
            if self.step_counter % 3 == 0 and buses:
                selected_bus = random.choice(buses)
                await self.generate_simulated_ai_event(db, selected_bus)

        finally:
            db.close()

    async def generate_simulated_ai_event(self, db: Session, bus: Bus):
        event_types = ["POTHOLE", "TRAFFIC_SPIKE", "WATERLOGGING", "PEDESTRIAN_SAFETY", "DAMAGED_SIGN"]
        chosen = random.choices(event_types, weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]

        bus.events_today_count += 1
        db.commit()

        if chosen == "POTHOLE":
            confidence = round(random.uniform(0.91, 0.98), 2)
            severity_val = "HIGH" if random.random() > 0.3 else "MEDIUM"
            cluster, is_new, defect = DefectClusteringService.cluster_defect_detection(
                db=db,
                bus_id=bus.bus_number,
                defect_type="POTHOLE",
                latitude=bus.current_lat + random.uniform(-0.0002, 0.0002),
                longitude=bus.current_lng + random.uniform(-0.0002, 0.0002),
                confidence=confidence,
                severity=severity_val,
                address_description=f"Route {bus.route.name if bus.route else 'Urban Corridor'}",
                evidence_image=f"/evidence/sample_pothole.jpg"
            )

            event_payload = {
                "type": "AI_DETECTION",
                "category": "POTHOLE",
                "bus_number": bus.bus_number,
                "cluster_code": cluster.cluster_code,
                "confirmed_buses": cluster.confirmed_buses_count,
                "total_detections": cluster.total_detections,
                "confidence": cluster.confidence,
                "severity": cluster.severity,
                "lat": cluster.latitude,
                "lng": cluster.longitude,
                "timestamp": datetime.utcnow().isoformat(),
                "is_clustered": not is_new
            }
            await ws_manager.broadcast_event(event_payload)

            if cluster.confirmed_buses_count >= 2:
                alert_payload = {
                    "type": "NEW_ALERT",
                    "severity": cluster.severity,
                    "title": f"Pothole Confirmed by Multiple Buses ({cluster.cluster_code})",
                    "message": f"Confirmed by {cluster.confirmed_buses_count} buses with {cluster.total_detections} detections at {cluster.address_description}.",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await ws_manager.broadcast_alert(alert_payload)

        elif chosen == "TRAFFIC_SPIKE":
            dens_val, dens_level = TrafficService.calculate_density(
                vehicle_count=random.randint(35, 60),
                avg_speed_kmh=random.uniform(8.0, 16.0)
            )
            event_payload = {
                "type": "TRAFFIC_UPDATE",
                "bus_number": bus.bus_number,
                "location_name": bus.route.name if bus.route else "Central Corridor",
                "density_percent": dens_val,
                "density_level": dens_level,
                "lat": bus.current_lat,
                "lng": bus.current_lng,
                "timestamp": datetime.utcnow().isoformat()
            }
            await ws_manager.broadcast_event(event_payload)

        elif chosen == "WATERLOGGING":
            cluster, is_new, defect = DefectClusteringService.cluster_defect_detection(
                db=db,
                bus_id=bus.bus_number,
                defect_type="WATERLOGGING",
                latitude=bus.current_lat,
                longitude=bus.current_lng,
                confidence=0.92,
                severity="HIGH",
                address_description=f"Underpass / Low-lying section near {bus.route.name if bus.route else 'Urban Hub'}",
                evidence_image=f"/evidence/sample_waterlogging.jpg"
            )
            await ws_manager.broadcast_event({
                "type": "AI_DETECTION",
                "category": "WATERLOGGING",
                "bus_number": bus.bus_number,
                "cluster_code": cluster.cluster_code,
                "severity": "HIGH",
                "lat": cluster.latitude,
                "lng": cluster.longitude,
                "timestamp": datetime.utcnow().isoformat()
            })

simulation_engine = SimulationEngine()
