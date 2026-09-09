import re
from typing import Optional, Dict, Any

class PlateOCRProvider:
    @staticmethod
    def validate_or_correct_plate(raw_plate: str, override_plate: Optional[str] = None) -> Dict[str, Any]:
        plate = (override_plate or raw_plate or "").strip().upper()
        cleaned = re.sub(r'[^A-Z0-9]', '', plate)
        is_valid = bool(re.match(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$', cleaned)) or len(cleaned) >= 6
        return {
            "is_valid": is_valid,
            "raw_plate": raw_plate,
            "final_plate": cleaned if cleaned else plate,
            "confidence": 0.98 if override_plate else 0.89
        }
