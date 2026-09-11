import math
import random
import uuid
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import RoadDefectCluster, RoadDefect, Alert

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class DefectClusteringService:
    @staticmethod
    def cluster_defect_detection(
        db: Session,
        bus_id: str,
        defect_type: str,
        latitude: float,
        longitude: float,
        confidence: float,
        severity: str,
        address_description: Optional[str] = None,
        evidence_image: Optional[str] = None,
        radius_meters: Optional[float] = None
    ) -> Tuple[RoadDefectCluster, bool, RoadDefect]:
        """
        Group nearby defect detections into a multi-bus confirmed cluster.
        Returns: (cluster, is_new_cluster, defect_record)
        """
        radius = radius_meters if radius_meters is not None else settings.DEFAULT_CLUSTERING_RADIUS_METERS

        # Query existing clusters of matching defect type
        existing_clusters = db.query(RoadDefectCluster).filter(
            RoadDefectCluster.defect_type == defect_type,
            RoadDefectCluster.status != "REPAIRED",
            RoadDefectCluster.status != "REJECTED"
        ).all()

        closest_cluster = None
        min_distance = float("inf")

        for cluster in existing_clusters:
            dist = haversine_distance_meters(latitude, longitude, cluster.latitude, cluster.longitude)
            if dist <= radius and dist < min_distance:
                min_distance = dist
                closest_cluster = cluster

        is_new_cluster = False

        if closest_cluster is not None:
            # Check if this bus has already reported this defect cluster
            prior_bus_report = db.query(RoadDefect).filter(
                RoadDefect.cluster_id == closest_cluster.id,
                RoadDefect.bus_id == bus_id
            ).first()

            if prior_bus_report is None:
                closest_cluster.confirmed_buses_count += 1

            total = closest_cluster.total_detections + 1
            closest_cluster.total_detections = total
            closest_cluster.last_detected_at = datetime.utcnow()

            # Refine coordinates with weighted average
            closest_cluster.latitude = (closest_cluster.latitude * (total - 1) + latitude) / total
            closest_cluster.longitude = (closest_cluster.longitude * (total - 1) + longitude) / total

            # Increase consensus confidence
            closest_cluster.confidence = min(0.99, max(closest_cluster.confidence, confidence) + 0.015)

            # Auto-escalate severity if multiple buses independently verify
            if closest_cluster.confirmed_buses_count >= 3:
                closest_cluster.severity = "CRITICAL"
            elif closest_cluster.confirmed_buses_count >= 2 and closest_cluster.severity == "LOW":
                closest_cluster.severity = "HIGH"

            if not closest_cluster.evidence_image and evidence_image:
                closest_cluster.evidence_image = evidence_image

            defect = RoadDefect(
                cluster_id=closest_cluster.id,
                bus_id=bus_id,
                defect_type=defect_type,
                latitude=latitude,
                longitude=longitude,
                confidence=confidence,
                severity=severity,
                detected_at=datetime.utcnow(),
                evidence_image=evidence_image
            )
            db.add(defect)
            db.commit()
            db.refresh(closest_cluster)
            db.refresh(defect)
            return closest_cluster, False, defect
        else:
            # Create a brand new defect cluster
            is_new_cluster = True
            cluster_code = f"RD-{uuid.uuid4().hex[:8].upper()}"

            cluster = RoadDefectCluster(
                cluster_code=cluster_code,
                defect_type=defect_type,
                latitude=latitude,
                longitude=longitude,
                confidence=confidence,
                severity=severity,
                status="UNRESOLVED",
                confirmed_buses_count=1,
                total_detections=1,
                first_detected_at=datetime.utcnow(),
                last_detected_at=datetime.utcnow(),
                address_description=address_description or f"Near GPS ({latitude:.4f}, {longitude:.4f})",
                evidence_image=evidence_image or f"/evidence/sample_{defect_type.lower()}.jpg"
            )
            db.add(cluster)
            db.flush()

            defect = RoadDefect(
                cluster_id=cluster.id,
                bus_id=bus_id,
                defect_type=defect_type,
                latitude=latitude,
                longitude=longitude,
                confidence=confidence,
                severity=severity,
                detected_at=datetime.utcnow(),
                evidence_image=evidence_image or cluster.evidence_image
            )
            db.add(defect)

            # If critical or high severity, trigger an automated city alert
            if severity in ["CRITICAL", "HIGH"]:
                alert_count = db.query(Alert).count() + 1
                alert = Alert(
                    alert_code=f"ALT-{1000 + alert_count}",
                    alert_type="POTHOLE_CRITICAL" if defect_type == "POTHOLE" else "INFRASTRUCTURE_DEFECT",
                    severity=severity,
                    title=f"New Road Defect Detected ({cluster_code})",
                    message=f"{defect_type.replace('_', ' ')} detected by {bus_id} at {cluster.address_description}. Confidence: {int(confidence * 100)}%.",
                    bus_id=bus_id,
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime.utcnow()
                )
                db.add(alert)

            db.commit()
            db.refresh(cluster)
            db.refresh(defect)
            return cluster, True, defect
