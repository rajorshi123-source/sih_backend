import random
from datetime import datetime, timedelta
from app.database import engine, SessionLocal, Base
from app.models.models import (
    User, Route, Bus, Camera, Detection,
    RoadDefectCluster, RoadDefect, TrafficEvent, Incident, Alert, Report
)
from app.services.auth_service import get_password_hash
from app.services.evidence_service import EvidenceService

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Ensure evidence directory & sample images exist
    EvidenceService.create_stock_evidence()

    db = SessionLocal()
    print("[Seed] Seeding Users with Role-Based Access...")

    # 1. Users
    users_data = [
        ("admin", "admin@bussense.ai", "Administrator", "Chief Administrator"),
        ("transport", "transport@bussense.ai", "Transport Authority", "Fleet Operations Director"),
        ("traffic", "traffic@bussense.ai", "Traffic Officer", "Senior Traffic Controller"),
        ("maintenance", "roads@bussense.ai", "Maintenance Officer", "Civil Infrastructure Engineer"),
        ("analyst", "analyst@bussense.ai", "Analyst", "Urban Intelligence Analyst")
    ]
    for username, email, role, full_name in users_data:
        user = User(
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            hashed_password=get_password_hash("password123")
        )
        db.add(user)

    print("[Seed] Seeding 8 Realistic Transit Routes...")
    # Coordinates in Kolkata Metro area
    routes_definitions = [
        {
            "name": "Howrah Station ⇄ Esplanade Central",
            "route_code": "R-101",
            "origin": "Howrah Station",
            "destination": "Esplanade Bus Terminus",
            "color": "#3b82f6",
            "distance_km": 6.8,
            "avg_journey_mins": 25,
            "waypoints": [
                [22.5850, 88.3426, "Howrah Station"],
                [22.5841, 88.3512, "Howrah Bridge West"],
                [22.5835, 88.3590, "Strand Road Approach"],
                [22.5760, 88.3530, "BBD Bagh North"],
                [22.5700, 88.3520, "Writers Building"],
                [22.5650, 88.3525, "Raj Bhavan"],
                [22.5645, 88.3512, "Curzon Park"],
                [22.5640, 88.3515, "Esplanade Terminus"]
            ]
        },
        {
            "name": "Salt Lake Sector V ⇄ Park Street",
            "route_code": "R-102",
            "origin": "Sector V IT Hub",
            "destination": "Park Street Metro",
            "color": "#10b981",
            "distance_km": 14.2,
            "avg_journey_mins": 45,
            "waypoints": [
                [22.5800, 88.4350, "College More Sector V"],
                [22.5750, 88.4200, "Karunamoyee Bus Station"],
                [22.5680, 88.4050, "Ultadanga EM Bypass Entry"],
                [22.5550, 88.3980, "Chingrighata Flyover"],
                [22.5480, 88.3900, "Science City Junction"],
                [22.5450, 88.3750, "Park Circus 7-Point"],
                [22.5510, 88.3520, "Park Street Crossing"]
            ]
        },
        {
            "name": "Garia Bus Stand ⇄ Esplanade",
            "route_code": "R-103",
            "origin": "Garia Bus Stand",
            "destination": "Esplanade",
            "color": "#f59e0b",
            "distance_km": 15.6,
            "avg_journey_mins": 50,
            "waypoints": [
                [22.4650, 88.3750, "Garia Bus Stand"],
                [22.4900, 88.3720, "Jadavpur 8B Bus Stand"],
                [22.5150, 88.3650, "Gariahat Crossing"],
                [22.5350, 88.3550, "Exide Crossing / Rabindra Sadan"],
                [22.5500, 88.3520, "Maidan West"],
                [22.5640, 88.3515, "Esplanade Terminus"]
            ]
        },
        {
            "name": "Dum Dum Metro ⇄ Howrah Station",
            "route_code": "R-104",
            "origin": "Dum Dum Junction",
            "destination": "Howrah Station",
            "color": "#8b5cf6",
            "distance_km": 11.4,
            "avg_journey_mins": 38,
            "waypoints": [
                [22.6220, 88.3780, "Dum Dum Station"],
                [22.6020, 88.3720, "Shyambazar 5-Point Crossing"],
                [22.5950, 88.3680, "Hatibagan Market"],
                [22.5850, 88.3640, "MG Road / Central Ave"],
                [22.5841, 88.3512, "Brabourne Road"],
                [22.5850, 88.3426, "Howrah Station"]
            ]
        },
        {
            "name": "New Town Eco Park ⇄ Sealdah Station",
            "route_code": "R-105",
            "origin": "Eco Park New Town",
            "destination": "Sealdah Railway Station",
            "color": "#ec4899",
            "distance_km": 16.0,
            "avg_journey_mins": 48,
            "waypoints": [
                [22.6050, 88.4650, "Eco Park Gate 1"],
                [22.5900, 88.4500, "New Town Bus Terminus"],
                [22.5750, 88.4200, "Salt Lake Bypass"],
                [22.5680, 88.3950, "Kankurgachi Crossing"],
                [22.5670, 88.3710, "Sealdah Flyover Approach"],
                [22.5665, 88.3700, "Sealdah Station Main"]
            ]
        },
        {
            "name": "Shyambazar ⇄ Jadavpur University",
            "route_code": "R-106",
            "origin": "Shyambazar 5-Point",
            "destination": "Jadavpur University 8B",
            "color": "#06b6d4",
            "distance_km": 13.5,
            "avg_journey_mins": 42,
            "waypoints": [
                [22.6020, 88.3720, "Shyambazar 5-Point"],
                [22.5820, 88.3700, "College Street Bata"],
                [22.5650, 88.3710, "Sealdah South"],
                [22.5380, 88.3680, "Ballygunge Phari"],
                [22.5150, 88.3650, "Gariahat Crossing"],
                [22.4900, 88.3720, "Jadavpur University"]
            ]
        },
        {
            "name": "Behala Chowrasta ⇄ BBD Bagh",
            "route_code": "R-107",
            "origin": "Behala Chowrasta",
            "destination": "BBD Bagh",
            "color": "#14b8a6",
            "distance_km": 12.0,
            "avg_journey_mins": 40,
            "waypoints": [
                [22.4980, 88.3180, "Behala Chowrasta"],
                [22.5180, 88.3220, "Taratala Crossing"],
                [22.5350, 88.3300, "Majerhat Bridge"],
                [22.5480, 88.3420, "Kidderpore Tram Depot"],
                [22.5620, 88.3480, "Babu Ghat"],
                [22.5700, 88.3520, "BBD Bagh"]
            ]
        },
        {
            "name": "Netaji Subhash Airport ⇄ Gariahat",
            "route_code": "R-108",
            "origin": "NSCBI Airport Gate 1",
            "destination": "Gariahat Mall",
            "color": "#6366f1",
            "distance_km": 21.0,
            "avg_journey_mins": 55,
            "waypoints": [
                [22.6520, 88.4460, "Airport Terminus"],
                [22.6200, 88.4350, "Kaikhali Crossing"],
                [22.5950, 88.4200, "Ultadanga Station"],
                [22.5680, 88.4050, "EM Bypass North"],
                [22.5480, 88.3900, "Science City"],
                [22.5280, 88.3750, "Ruby Hospital Crossing"],
                [22.5150, 88.3650, "Gariahat Junction"]
            ]
        }
    ]

    saved_routes = []
    for r_def in routes_definitions:
        route = Route(
            name=r_def["name"],
            route_code=r_def["route_code"],
            origin=r_def["origin"],
            destination=r_def["destination"],
            color=r_def["color"],
            distance_km=r_def["distance_km"],
            avg_journey_mins=r_def["avg_journey_mins"],
            waypoints_json=r_def["waypoints"]
        )
        db.add(route)
        saved_routes.append(route)

    db.flush()

    print("[Seed] Seeding 24 Intelligent Buses with 5-Camera Arrays (including BUS-024)...")
    # 24 buses
    saved_buses = []
    for i in range(1, 25):
        bus_num = f"BUS-{i:03d}"
        reg_num = f"WB-04-E-{1000 + i}"
        route = saved_routes[i % len(saved_routes)]
        wp = route.waypoints_json[i % len(route.waypoints_json)]

        status = "ACTIVE"
        if i in [18]:
            status = "MAINTENANCE"
        elif i in [19, 20]:
            status = "INACTIVE"

        cam_status = "ONLINE"
        ai_status = "ONLINE"
        if i == 15:
            cam_status = "DEGRADED"
        elif i == 18:
            cam_status = "OFFLINE"
            ai_status = "OFFLINE"

        bus = Bus(
            bus_number=bus_num,
            registration_number=reg_num,
            route_id=route.id,
            current_lat=wp[0] + random.uniform(-0.0003, 0.0003),
            current_lng=wp[1] + random.uniform(-0.0003, 0.0003),
            speed_kmh=round(random.uniform(20.0, 42.0), 1) if status == "ACTIVE" else 0.0,
            heading=random.choice([45.0, 90.0, 180.0, 270.0]),
            status=status,
            camera_status=cam_status,
            ai_status=ai_status,
            events_today_count=random.randint(12, 64) if status == "ACTIVE" else 0,
            current_waypoint_index=i % len(route.waypoints_json),
            direction_forward=True
        )
        db.add(bus)
        db.flush()
        saved_buses.append(bus)

        # Add 5 cameras for each bus (FRONT, REAR, LEFT, RIGHT, CABIN)
        for pos in ["FRONT", "REAR", "LEFT", "RIGHT", "CABIN"]:
            cam = Camera(
                bus_id=bus.id,
                position=pos,
                resolution="1080p",
                fps=30,
                status="ONLINE" if cam_status != "OFFLINE" else "OFFLINE"
            )
            db.add(cam)

    print("[Seed] Seeding Multi-Bus Defect Clusters (Potholes, Waterlogging, Signs)...")
    # Defect Clusters with multiple confirming buses to showcase the intelligent clustering
    clusters_data = [
        {
            "code": "RD-1024",
            "type": "POTHOLE",
            "lat": 22.5726,
            "lng": 88.3639,
            "severity": "CRITICAL",
            "status": "UNRESOLVED",
            "conf": 0.97,
            "buses_count": 4,
            "detections": 11,
            "address": "MG Road Crossing near Central Avenue",
            "evidence": "/evidence/sample_pothole.jpg"
        },
        {
            "code": "RD-1025",
            "type": "WATERLOGGING",
            "lat": 22.5850,
            "lng": 88.4100,
            "severity": "HIGH",
            "status": "UNDER_REVIEW",
            "conf": 0.94,
            "buses_count": 3,
            "detections": 7,
            "address": "Ultadanga Underpass / VIP Road Junction",
            "evidence": "/evidence/sample_waterlogging.jpg"
        },
        {
            "code": "RD-1026",
            "type": "DAMAGED_ROAD",
            "lat": 22.5510,
            "lng": 88.3520,
            "severity": "HIGH",
            "status": "WORK_ORDER_ISSUED",
            "conf": 0.89,
            "buses_count": 2,
            "detections": 5,
            "address": "Park Street Metro Approach (Lane 2)",
            "evidence": "/evidence/sample_damaged_road.jpg"
        },
        {
            "code": "RD-1027",
            "type": "MISSING_DIVIDER",
            "lat": 22.5680,
            "lng": 88.4050,
            "severity": "MEDIUM",
            "status": "UNRESOLVED",
            "conf": 0.91,
            "buses_count": 3,
            "detections": 8,
            "address": "EM Bypass North near Salt Lake Gate",
            "evidence": "/evidence/sample_damaged_road.jpg"
        },
        {
            "code": "RD-1028",
            "type": "DAMAGED_SIGN",
            "lat": 22.5841,
            "lng": 88.3512,
            "severity": "LOW",
            "status": "REPAIRED",
            "conf": 0.95,
            "buses_count": 1,
            "detections": 3,
            "address": "Howrah Bridge West Approach Speed Sign",
            "evidence": "/evidence/sample_damaged_road.jpg"
        },
        {
            "code": "RD-1029",
            "type": "POTHOLE",
            "lat": 22.5350,
            "lng": 88.3550,
            "severity": "HIGH",
            "status": "UNRESOLVED",
            "conf": 0.93,
            "buses_count": 2,
            "detections": 6,
            "address": "Rabindra Sadan / Exide Southbound Lane",
            "evidence": "/evidence/sample_pothole.jpg"
        },
        {
            "code": "RD-1030",
            "type": "MISSING_ZEBRA",
            "lat": 22.5645,
            "lng": 88.3512,
            "severity": "MEDIUM",
            "status": "UNRESOLVED",
            "conf": 0.88,
            "buses_count": 2,
            "detections": 4,
            "address": "Esplanade Tram Crossing Pedestrian Zone",
            "evidence": "/evidence/sample_damaged_road.jpg"
        },
        {
            "code": "RD-1031",
            "type": "WATERLOGGING",
            "lat": 22.5480,
            "lng": 88.3900,
            "severity": "HIGH",
            "status": "UNRESOLVED",
            "conf": 0.96,
            "buses_count": 3,
            "detections": 9,
            "address": "Science City Service Road Drainage Choke",
            "evidence": "/evidence/sample_waterlogging.jpg"
        }
    ]

    saved_clusters = []
    for c_data in clusters_data:
        cluster = RoadDefectCluster(
            cluster_code=c_data["code"],
            defect_type=c_data["type"],
            latitude=c_data["lat"],
            longitude=c_data["lng"],
            severity=c_data["severity"],
            status=c_data["status"],
            confidence=c_data["conf"],
            confirmed_buses_count=c_data["buses_count"],
            total_detections=c_data["detections"],
            address_description=c_data["address"],
            evidence_image=c_data["evidence"],
            first_detected_at=datetime.utcnow() - timedelta(hours=random.randint(6, 48)),
            last_detected_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 60))
        )
        db.add(cluster)
        saved_clusters.append(cluster)
        db.flush()

        # Seed sub-detections for each cluster from multiple buses
        for b_idx in range(c_data["buses_count"]):
            bus_reporting = saved_buses[b_idx % len(saved_buses)]
            defect = RoadDefect(
                cluster_id=cluster.id,
                bus_id=bus_reporting.bus_number,
                defect_type=c_data["type"],
                latitude=c_data["lat"] + random.uniform(-0.0001, 0.0001),
                longitude=c_data["lng"] + random.uniform(-0.0001, 0.0001),
                confidence=round(random.uniform(0.88, 0.98), 2),
                severity=c_data["severity"],
                detected_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 180)),
                evidence_image=c_data["evidence"]
            )
            db.add(defect)

    print("[Seed] Seeding Traffic Events & Congestion Hotspots...")
    traffic_locations = [
        ("Howrah Bridge Approach", 22.5841, 88.3512, 88, "SEVERE", 11.2, 54),
        ("Park Circus 7-Point Crossing", 22.5450, 88.3750, 84, "HIGH", 14.5, 48),
        ("Shyambazar 5-Point Crossing", 22.6020, 88.3720, 78, "HIGH", 16.0, 42),
        ("Gariahat Junction", 22.5150, 88.3650, 68, "HIGH", 18.2, 38),
        ("College More Sector V", 22.5800, 88.4350, 82, "HIGH", 13.8, 50),
        ("Chingrighata EM Bypass", 22.5550, 88.3980, 92, "SEVERE", 8.5, 62),
        ("Exide Crossing / Rabindra Sadan", 22.5350, 88.3550, 62, "MEDIUM", 22.0, 32),
        ("Esplanade Dorina Crossing", 22.5640, 88.3515, 87, "HIGH", 12.0, 52)
    ]
    for loc_name, lat, lng, dens, level, spd, veh in traffic_locations:
        te = TrafficEvent(
            bus_id=random.choice(saved_buses).bus_number,
            location_name=loc_name,
            latitude=lat,
            longitude=lng,
            density_percent=dens,
            density_level=level,
            avg_speed_kmh=spd,
            vehicle_count=veh,
            cars_count=int(veh * 0.45),
            bikes_count=int(veh * 0.28),
            buses_count=int(veh * 0.08),
            trucks_count=int(veh * 0.05),
            autos_count=int(veh * 0.14),
            duration_minutes=random.randint(15, 45),
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 60))
        )
        db.add(te)

    print("[Seed] Seeding Incidents (Hit-and-Run, Rash Driving, Pedestrian Safety)...")
    incidents_data = [
        {
            "code": "INC-2026-0012",
            "type": "HIT_AND_RUN",
            "severity": "CRITICAL",
            "bus": "BUS-024",
            "track_id": "TRK-8821",
            "plate": "WB12AB1234",
            "plate_conf": 0.91,
            "trk_conf": 0.88,
            "lat": 22.5697,
            "lng": 88.3697,
            "location": "Central Avenue near Bowbazar Crossing",
            "status": "NEW",
            "evidence": "/evidence/sample_hit_and_run.jpg",
            "notes": "Silver sedan clipped stationary auto-rickshaw and fled north at high velocity. Rear plate captured by FRONT camera."
        },
        {
            "code": "INC-2026-0013",
            "type": "RASH_DRIVING",
            "severity": "HIGH",
            "bus": "BUS-017",
            "track_id": "TRK-7412",
            "plate": "WB02X9876",
            "plate_conf": 0.89,
            "trk_conf": 0.92,
            "lat": 22.5480,
            "lng": 88.3900,
            "location": "EM Bypass Science City Overpass",
            "status": "UNDER_REVIEW",
            "evidence": "/evidence/sample_rash_driving.jpg",
            "notes": "Erratic swerving across 3 lanes at 74 km/h in 40 km/h zone, cutting across bus right blindspot."
        },
        {
            "code": "INC-2026-0014",
            "type": "PEDESTRIAN_SAFETY_RISK",
            "severity": "HIGH",
            "bus": "BUS-003",
            "track_id": "TRK-9120",
            "plate": None,
            "plate_conf": 0.0,
            "trk_conf": 0.95,
            "lat": 22.5600,
            "lng": 88.3800,
            "location": "Sealdah Flyover Base School Zone",
            "status": "VERIFIED",
            "evidence": "/evidence/sample_pedestrian.jpg",
            "notes": "School student stepped into blind road sector while vehicles approached at 35 km/h."
        },
        {
            "code": "INC-2026-0015",
            "type": "ROAD_HAZARD",
            "severity": "MEDIUM",
            "bus": "BUS-008",
            "track_id": None,
            "plate": None,
            "plate_conf": 0.0,
            "trk_conf": 0.85,
            "lat": 22.5750,
            "lng": 88.4200,
            "location": "Karunamoyee Terminus Approach",
            "status": "RESOLVED",
            "evidence": "/evidence/sample_damaged_road.jpg",
            "notes": "Fallen construction barrier blocking left-hand traffic lane. Traffic police notified and cleared."
        }
    ]
    for inc in incidents_data:
        record = Incident(
            incident_code=inc["code"],
            incident_type=inc["type"],
            severity=inc["severity"],
            bus_id=inc["bus"],
            vehicle_track_id=inc["track_id"],
            detected_plate=inc["plate"],
            corrected_plate=None,
            plate_confidence=inc["plate_conf"],
            tracking_confidence=inc["trk_conf"],
            latitude=inc["lat"],
            longitude=inc["lng"],
            location_name=inc["location"],
            status=inc["status"],
            evidence_image=inc["evidence"],
            notes=inc["notes"],
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(12, 140))
        )
        db.add(record)

    print("[Seed] Seeding High-Priority Urban Intelligence Alerts...")
    alerts_data = [
        ("ALT-1001", "HIT_AND_RUN", "CRITICAL", "High Priority Hit-and-Run Alert (INC-2026-0012)", "Vehicle WB12AB1234 flagged exiting scene at Bowbazar. Law enforcement alerted.", "BUS-024", 22.5697, 88.3697),
        ("ALT-1002", "POTHOLE_CRITICAL", "CRITICAL", "Dangerous Crater Pothole Cluster RD-1024", "Confirmed by 4 buses with 11 detections on MG Road. Tire damage risk.", "BUS-024", 22.5726, 88.3639),
        ("ALT-1003", "CONGESTION_SEVERE", "HIGH", "Severe Traffic Bottleneck at Chingrighata", "Traffic density 92% with average speed down to 8.5 km/h. Journey delay +22m.", "BUS-002", 22.5550, 88.3980),
        ("ALT-1004", "WATERLOGGING_SEVERE", "HIGH", "Flooding Detected at Ultadanga Underpass", "3 buses report standing water >15cm. Lane 1 and 2 submerged.", "BUS-011", 22.5850, 88.4100),
        ("ALT-1005", "RASH_DRIVING", "HIGH", "Reckless Driving Incident (WB02X9876)", "Erratic overtaking and lane cut detected by BUS-017 on EM Bypass.", "BUS-017", 22.5480, 88.3900),
        ("ALT-1006", "PEDESTRIAN_RISK", "MEDIUM", "School Child Crossing Near Traffic Zone", "Near-miss proximity event detected in Sealdah school corridor.", "BUS-003", 22.5600, 88.3800)
    ]
    for code, a_type, sev, title, msg, bus, lat, lng in alerts_data:
        al = Alert(
            alert_code=code,
            alert_type=a_type,
            severity=sev,
            title=title,
            message=msg,
            bus_id=bus,
            latitude=lat,
            longitude=lng,
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 90)),
            is_read=False,
            is_acknowledged=False
        )
        db.add(al)

    # Historical Reports
    report = Report(
        report_type="ROAD_HEALTH",
        title="Weekly City Road Surface Defect Audit",
        period_start=datetime.utcnow() - timedelta(days=7),
        period_end=datetime.utcnow(),
        generated_by="Administrator",
        summary_json={
            "total_defects_detected": 247,
            "potholes": 184,
            "waterlogging": 38,
            "infrastructure_damage": 25,
            "clusters_formed": 42,
            "repaired_this_week": 18
        }
    )
    db.add(report)

    db.commit()
    db.close()
    print("[Seed] Successfully seeded BusSense AI database with rich demonstration data!")

if __name__ == "__main__":
    seed_database()
