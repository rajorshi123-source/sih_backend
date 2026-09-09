import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "active_buses" in data
    assert "potholes_detected" in data
    assert "recent_events" in data
    assert len(data["recent_events"]) > 0

def test_get_buses():
    response = client.get("/api/buses")
    assert response.status_code == 200
    buses = response.json()
    assert len(buses) >= 20
    assert buses[0]["bus_number"].startswith("BUS-")

def test_get_single_bus():
    response = client.get("/api/buses/BUS-024")
    assert response.status_code == 200
    bus = response.json()
    assert bus["bus_number"] == "BUS-024"
    assert len(bus["cameras"]) == 5

def test_routes_and_od_matrix():
    r_resp = client.get("/api/routes")
    assert r_resp.status_code == 200
    assert len(r_resp.json()) == 8

    rank_resp = client.get("/api/routes/analytics/ranking")
    assert rank_resp.status_code == 200
    assert len(rank_resp.json()) == 8

    od_resp = client.get("/api/routes/od-matrix")
    assert od_resp.status_code == 200
    assert od_resp.json()["is_demo_data"] is True

def test_road_defects_and_clustering():
    defects_resp = client.get("/api/road-defects")
    assert defects_resp.status_code == 200
    defects = defects_resp.json()
    assert len(defects) > 0

    # Test reporting a new defect near an existing cluster to test multi-bus clustering
    cluster = defects[0]
    new_defect_payload = {
        "bus_id": "BUS-019",
        "defect_type": cluster["defect_type"],
        "latitude": cluster["latitude"] + 0.00005,  # ~5m away
        "longitude": cluster["longitude"] + 0.00005,
        "confidence": 0.95,
        "severity": "HIGH"
    }
    report_resp = client.post("/api/road-defects", json=new_defect_payload)
    assert report_resp.status_code == 200
    updated_cluster = report_resp.json()
    assert updated_cluster["cluster_code"] == cluster["cluster_code"]
    assert updated_cluster["total_detections"] >= cluster["total_detections"]

def test_traffic_intelligence():
    summary_resp = client.get("/api/traffic/summary")
    assert summary_resp.status_code == 200
    assert "overall_density_percent" in summary_resp.json()

    bottlenecks_resp = client.get("/api/traffic/bottlenecks")
    assert bottlenecks_resp.status_code == 200
    assert len(bottlenecks_resp.json()) > 0

def test_incidents_and_ocr_correction():
    inc_resp = client.get("/api/incidents")
    assert inc_resp.status_code == 200
    incidents = inc_resp.json()
    assert len(incidents) > 0

    target_inc = incidents[0]
    # Test OCR plate correction
    patch_resp = client.patch(
        f"/api/incidents/{target_inc['id']}/ocr-correct",
        json={"corrected_plate": "WB12AB9999", "notes": "Verified by supervisor test"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["corrected_plate"] == "WB12AB9999"

def test_alerts_management():
    alerts_resp = client.get("/api/alerts")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) > 0

    first_alert = alerts[0]
    ack_resp = client.patch(
        f"/api/alerts/{first_alert['id']}/acknowledge",
        json={"acknowledged_by": "Test Supervisor"}
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["is_acknowledged"] is True

def test_video_analysis():
    response = client.post(
        "/api/video/analyze",
        data={"scenario_id": "pothole-downtown", "bus_id": "BUS-024"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_frames"] == 15
    assert len(data["frame_results"]) == 15
    assert len(data["summary_events"]) > 0

def test_simulation_control():
    # Test speed change
    ctrl_resp = client.post("/api/simulation/control", json={"action": "set_speed", "speed_multiplier": 2.0})
    assert ctrl_resp.status_code == 200

    # Test defect trigger
    trigger_resp = client.post("/api/simulation/control", json={"action": "trigger_defect", "defect_type": "POTHOLE"})
    assert trigger_resp.status_code == 200
    assert "cluster_code" in trigger_resp.json()
