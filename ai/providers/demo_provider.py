import random
from typing import List, Dict, Any

class DemoAIProvider:
    def __init__(self):
        self.classes = ["car", "motorcycle", "bus", "truck", "auto_rickshaw", "pedestrian"]

    def detect_objects(self, frame_number: int) -> List[Dict[str, Any]]:
        random.seed(frame_number)
        num_objects = random.randint(3, 6)
        detections = []

        for idx in range(num_objects):
            cname = random.choice(self.classes)
            x1 = random.randint(50, 500)
            y1 = random.randint(100, 350)
            w = random.randint(60, 150)
            h = random.randint(40, 120)
            bbox = [x1, y1, x1 + w, y1 + h]
            conf = round(random.uniform(0.78, 0.98), 2)

            det: Dict[str, Any] = {
                "class_name": cname,
                "confidence": conf,
                "bbox": bbox,
                "speed_estimate_kmh": round(random.uniform(20.0, 55.0), 1),
                "plate_text": f"WB{random.randint(10, 99)}A{random.randint(1000, 9999)}" if cname in ["car", "bus", "truck"] else None
            }
            detections.append(det)

        # Ensure pothole defect on frames 40 and 50 (i=4, 5)
        if frame_number in [40, 50]:
            detections.append({
                "class_name": "car",
                "confidence": 0.94,
                "bbox": [320, 280, 440, 360],
                "defect_type": "POTHOLE",
                "speed_estimate_kmh": 22.0
            })

        # Ensure school child / pedestrian risk on frames 80 and 90 (i=8, 9)
        if frame_number in [80, 90]:
            detections.append({
                "class_name": "pedestrian",
                "confidence": 0.96,
                "bbox": [200, 240, 260, 380],
                "is_school_child": True,
                "speed_estimate_kmh": 4.5
            })

        return detections

    def track_vehicles(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tracked = []
        for idx, det in enumerate(detections):
            d = dict(det)
            d["track_id"] = 100 + idx
            tracked.append(d)
        return tracked

