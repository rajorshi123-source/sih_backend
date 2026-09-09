import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from app.config import settings

class EvidenceService:
    @staticmethod
    def ensure_evidence_directory():
        os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)

    @staticmethod
    def generate_synthetic_evidence(
        event_type: str,
        bus_number: str,
        gps_lat: float,
        gps_lng: float,
        confidence: float,
        subtext: str = ""
    ) -> str:
        """
        Generate a dashcam evidence image with telemetry overlay and bounding box.
        Returns the web URL path (e.g. /evidence/sample_pothole_1.jpg).
        """
        EvidenceService.ensure_evidence_directory()
        filename = f"evidence_{event_type.lower()}_{bus_number.lower()}_{int(datetime.utcnow().timestamp())}.jpg"
        filepath = os.path.join(settings.EVIDENCE_DIR, filename)

        width, height = 800, 480
        # Background: asphalt dark gray gradient
        img = Image.new("RGB", (width, height), color=(35, 40, 45))
        draw = ImageDraw.Draw(img)

        # Draw simulated road horizon & road surface
        draw.rectangle([0, int(height * 0.45), width, height], fill=(45, 48, 52))
        # Road lane lines
        for y in range(int(height * 0.5), height, 40):
            draw.line([(width * 0.5, y), (width * 0.5, y + 25)], fill=(230, 230, 200), width=4)

        # Draw visual feature depending on event_type
        if "POTHOLE" in event_type.upper():
            # Draw pothole ellipse with dark crater and shadow
            box = [int(width * 0.42), int(height * 0.65), int(width * 0.58), int(height * 0.78)]
            draw.ellipse(box, fill=(18, 18, 20), outline=(20, 20, 22))
            draw.ellipse([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5], fill=(10, 10, 12))
            # AI Bounding Box (Red/Amber)
            draw.rectangle([box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10], outline=(239, 68, 68), width=3)
            draw.rectangle([box[0] - 10, box[1] - 30, box[0] + 160, box[1] - 10], fill=(239, 68, 68))
            draw.text((box[0] - 5, box[1] - 28), f"POTHOLE {int(confidence*100)}%", fill=(255, 255, 255))
        elif "WATERLOGGING" in event_type.upper():
            # Water surface reflection
            box = [int(width * 0.3), int(height * 0.6), int(width * 0.7), int(height * 0.85)]
            draw.ellipse(box, fill=(30, 60, 90), outline=(40, 90, 140))
            draw.rectangle([box[0] - 5, box[1] - 5, box[2] + 5, box[3] + 5], outline=(59, 130, 246), width=3)
            draw.rectangle([box[0] - 5, box[1] - 28, box[0] + 200, box[1] - 5], fill=(59, 130, 246))
            draw.text((box[0], box[1] - 26), f"WATERLOGGING {int(confidence*100)}%", fill=(255, 255, 255))
        elif "PLATE" in event_type.upper() or "HIT_AND_RUN" in event_type.upper():
            # Vehicle rear and number plate
            draw.rectangle([int(width * 0.35), int(height * 0.4), int(width * 0.65), int(height * 0.75)], fill=(60, 65, 75))
            plate_box = [int(width * 0.44), int(height * 0.62), int(width * 0.56), int(height * 0.68)]
            draw.rectangle(plate_box, fill=(255, 255, 255), outline=(0, 0, 0), width=2)
            draw.text((plate_box[0] + 10, plate_box[1] + 5), subtext or "WB12AB1234", fill=(0, 0, 0))
            draw.rectangle([plate_box[0] - 4, plate_box[1] - 4, plate_box[2] + 4, plate_box[3] + 4], outline=(234, 179, 8), width=2)
            draw.rectangle([plate_box[0] - 4, plate_box[1] - 25, plate_box[0] + 150, plate_box[1] - 4], fill=(234, 179, 8))
            draw.text((plate_box[0], plate_box[1] - 22), f"OCR: {int(confidence*100)}%", fill=(0, 0, 0))
        else:
            # Generic traffic / pedestrian bounding box
            box = [int(width * 0.45), int(height * 0.5), int(width * 0.55), int(height * 0.8)]
            draw.rectangle(box, outline=(16, 185, 129), width=3)
            draw.rectangle([box[0], box[1] - 24, box[0] + 140, box[1]], fill=(16, 185, 129))
            draw.text((box[0] + 5, box[1] - 22), f"{event_type} {int(confidence*100)}%", fill=(0, 0, 0))

        # Dashcam HUD Overlay: Bus, Camera, GPS, Timestamp
        hud_bar = [0, 0, width, 40]
        draw.rectangle(hud_bar, fill=(0, 0, 0, 180))
        ts_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        hud_text = f"BUSSENSE AI | {bus_number} [FRONT-CAM-01] | GPS: {gps_lat:.5f}, {gps_lng:.5f} | {ts_str}"
        draw.text((15, 12), hud_text, fill=(0, 255, 180))

        # Bottom banner with model tag
        draw.rectangle([0, height - 30, width, height], fill=(0, 0, 0, 200))
        draw.text((15, height - 22), f"EDGE-AI INFERENCE ENGINE v2.4 | CONF: {confidence:.2f} | EVENT: {event_type}", fill=(200, 220, 240))

        img.save(filepath, "JPEG", quality=85)
        return f"/evidence/{filename}"

    @staticmethod
    def create_stock_evidence():
        """Ensure default sample evidence images are generated on startup."""
        EvidenceService.ensure_evidence_directory()
        samples = [
            ("POTHOLE", "BUS-024", 22.5726, 88.3639, 0.94, ""),
            ("WATERLOGGING", "BUS-011", 22.5850, 88.4100, 0.91, ""),
            ("DAMAGED_ROAD", "BUS-007", 22.5500, 88.3500, 0.88, ""),
            ("HIT_AND_RUN", "BUS-024", 22.5697, 88.3697, 0.91, "WB12AB1234"),
            ("RASH_DRIVING", "BUS-017", 22.5400, 88.3700, 0.86, "WB02X9876"),
            ("PEDESTRIAN", "BUS-003", 22.5600, 88.3800, 0.96, "")
        ]
        for ev_type, bus, lat, lng, conf, txt in samples:
            target = os.path.join(settings.EVIDENCE_DIR, f"sample_{ev_type.lower()}.jpg")
            if not os.path.exists(target):
                # Generate and copy/save directly to standard sample name
                EvidenceService.generate_synthetic_evidence(ev_type, bus, lat, lng, conf, txt)
