from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import RoadDefectCluster, RoadDefect
from app.schemas.schemas import RoadDefectClusterResponse, RoadDefectCreate
from app.services.clustering_service import DefectClusteringService

router = APIRouter(prefix="/road-defects", tags=["Road Health & Defect Clustering"])

@router.get("", response_model=List[RoadDefectClusterResponse])
def get_all_defect_clusters(
    defect_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RoadDefectCluster)
    if defect_type:
        query = query.filter(RoadDefectCluster.defect_type == defect_type)
    if severity:
        query = query.filter(RoadDefectCluster.severity == severity)
    if status:
        query = query.filter(RoadDefectCluster.status == status)

    return query.order_by(RoadDefectCluster.last_detected_at.desc()).all()

@router.get("/{defect_id}")
def get_defect_cluster_detail(defect_id: str, db: Session = Depends(get_db)):
    cluster = db.query(RoadDefectCluster).filter(
        (RoadDefectCluster.id == defect_id) | (RoadDefectCluster.cluster_code == defect_id)
    ).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Road defect cluster not found")

    defects = db.query(RoadDefect).filter(RoadDefect.cluster_id == cluster.id).all()
    confirming_buses = list(set([d.bus_id for d in defects]))

    return {
        "cluster": cluster,
        "confirming_buses": confirming_buses,
        "detection_history": [
            {
                "id": d.id,
                "bus_id": d.bus_id,
                "confidence": d.confidence,
                "severity": d.severity,
                "detected_at": d.detected_at,
                "lat": d.latitude,
                "lng": d.longitude
            } for d in defects
        ]
    }

@router.post("", response_model=RoadDefectClusterResponse)
def report_new_defect(payload: RoadDefectCreate, db: Session = Depends(get_db)):
    cluster, is_new, defect = DefectClusteringService.cluster_defect_detection(
        db=db,
        bus_id=payload.bus_id,
        defect_type=payload.defect_type,
        latitude=payload.latitude,
        longitude=payload.longitude,
        confidence=payload.confidence,
        severity=payload.severity,
        evidence_image=payload.evidence_image
    )
    return cluster

@router.patch("/{defect_id}/status")
def update_defect_status(defect_id: str, status: str, db: Session = Depends(get_db)):
    cluster = db.query(RoadDefectCluster).filter(
        (RoadDefectCluster.id == defect_id) | (RoadDefectCluster.cluster_code == defect_id)
    ).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Road defect cluster not found")

    cluster.status = status.upper()
    db.commit()
    db.refresh(cluster)
    return {"message": "Status updated successfully", "cluster": cluster}
