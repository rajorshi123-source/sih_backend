import uuid
import random
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Bus
from app.schemas.schemas import VideoAnalysisResponse, VideoFrameResult, DetectionBox
from ai.providers.demo_provider import DemoAIProvider

router = APIRouter(prefix="/video", tags=["AI Video Analysis"])

ai_provider = DemoAIProvider()

DEMO_SCENARIOS = [
    {
        "id": "pothole-downtown",
        "title": "Downtown Pothole & Road Defect Detection",
        "bus_id": "BUS-024",
        "route_code": "R-101",
        "location": "MG Road / Central Avenue Corridor",
        "duration_sec": 12.0,
        "description": "High-confidence detection of deep crater pothole with auto-clustering and telemetry geotagging."
    },
    {
        "id": "traffic-bottleneck",
        "title": "Peak Evening Traffic Density & Congestion",
        "bus_id": "BUS-017",
        "route_code": "R-102",
        "location": "Park Circus 7-Point Crossing",
        "duration_sec": 15.0,
        "description": "Real-time vehicle counting, density estimation (88%), and bottleneck delay profiling."
    },
    {
        "id": "pedestrian-risk",
        "title": "School Zone Pedestrian Safety & Crossing Risk",
        "bus_id": "BUS-003",
        "route_code": "R-105",
        "location": "Sealdah School Zone Crossing",
        "duration_sec": 10.0,
        "description": "Pedestrian proximity monitoring, child risk detection, and safe braking distance verification."
    },
    {
        "id": "hit-and-run",
        "title": "Hit-and-Run Collision & License Plate OCR",
        "bus_id": "BUS-024",
        "route_code": "R-101",
        "location": "Bowbazar Crossing",
        "duration_sec": 14.0,
        "description": "Side collision tracking, escaping vehicle trajectory, and 91% confidence license plate recognition."
    }
]

@router.get("/samples")
def get_sample_videos():
    return DEMO_SCENARIOS

@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(
    scenario_id: Optional[str] = Form(None),
    bus_id: Optional[str] = Form("BUS-024"),
    video_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    session_id = f"VSS-{uuid.uuid4().hex[:8].upper()}"
    selected_scenario = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), DEMO_SCENARIOS[0])

    bus_num = bus_id or selected_scenario["bus_id"]
    route_code = selected_scenario["route_code"]

    # Generate 15 representative frames with high-fidelity detections
    frame_results = []
    events_generated = 0
    summary_events = []

    for i in range(1, 16):
        timestamp_sec = round((i - 1) * 0.8, 2)
        detections_raw = ai_provider.detect_objects(frame_number=i * 10)
        tracked = ai_provider.track_vehicles(detections_raw)

        det_boxes = []
        veh_counts = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0, "auto_rickshaw": 0, "pedestrian": 0}
        safety_alerts = []

        for det in tracked:
            cname = det["class_name"]
            if cname in veh_counts:
                veh_counts[cname] += 1

            det_boxes.append(DetectionBox(
                class_name=cname,
                confidence=det["confidence"],
                bbox=det["bbox"],
                track_id=det.get("track_id"),
                speed_estimate_kmh=det.get("speed_estimate_kmh"),
                plate_text=det.get("plate_text")
            ))

            if det.get("defect_type") == "POTHOLE" and i in [4, 5]:
                events_generated += 1
                summary_events.append({
                    "frame": i,
                    "type": "POTHOLE_DETECTED",
                    "confidence": f"{int(det['confidence']*100)}%",
                    "severity": "HIGH",
                    "bbox": det["bbox"],
                    "gps": [22.5726, 88.3639],
                    "evidence_image": "/evidence/sample_pothole.jpg"
                })

            if det.get("is_school_child") and i in [8, 9]:
                events_generated += 1
                safety_alerts.append("PEDESTRIAN_SAFETY_RISK: School Child in Road Zone")
                summary_events.append({
                    "frame": i,
                    "type": "PEDESTRIAN_RISK",
                    "confidence": f"{int(det['confidence']*100)}%",
                    "severity": "HIGH",
                    "gps": [22.5600, 88.3800],
                    "evidence_image": "/evidence/sample_pedestrian.jpg"
                })

        density_pct = min(95, 30 + sum(veh_counts.values()) * 12)

        frame_results.append(VideoFrameResult(
            frame_number=i,
            timestamp_sec=timestamp_sec,
            detections=det_boxes,
            vehicle_counts=veh_counts,
            density_percent=density_pct,
            safety_alerts=safety_alerts
        ))

    # Add plate recognition event if scenario is hit-and-run
    if scenario_id == "hit-and-run" or not summary_events:
        summary_events.append({
            "frame": 6,
            "type": "PLATE_OCR_CAPTURED",
            "plate": "WB12AB1234",
            "confidence": "91%",
            "severity": "CRITICAL",
            "gps": [22.5697, 88.3697],
            "evidence_image": "/evidence/sample_hit_and_run.jpg"
        })
        events_generated += 1

    return {
        "session_id": session_id,
        "video_name": video_file.filename if video_file else f"{selected_scenario['id']}.mp4",
        "total_frames": 15,
        "processed_frames": 15,
        "fps": 25.0,
        "duration_seconds": 12.0,
        "events_generated": events_generated,
        "frame_results": frame_results,
        "summary_events": summary_events,
        "bus_id": bus_num,
        "route_code": route_code
    }
