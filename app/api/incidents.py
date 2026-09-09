from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Incident
from app.schemas.schemas import (
    IncidentResponse, IncidentStatusUpdate, IncidentOCRCorrection
)
from ai.providers.ocr_provider import PlateOCRProvider

router = APIRouter(prefix="/incidents", tags=["Incidents & Law Enforcement"])

@router.get("", response_model=List[IncidentResponse])
def get_all_incidents(
    status: Optional[str] = None,
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)
    if severity:
        query = query.filter(Incident.severity == severity)

    return query.order_by(Incident.timestamp.desc()).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_detail(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_code == incident_id)
    ).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(incident_id: str, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_code == incident_id)
    ).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.status = payload.status.upper()
    if payload.notes:
        inc.notes = (inc.notes or "") + f"\n[{payload.status}]: {payload.notes}"
    db.commit()
    db.refresh(inc)
    return inc

@router.patch("/{incident_id}/ocr-correct", response_model=IncidentResponse)
def correct_incident_ocr_plate(incident_id: str, payload: IncidentOCRCorrection, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(
        (Incident.id == incident_id) | (Incident.incident_code == incident_id)
    ).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    validation = PlateOCRProvider.validate_or_correct_plate(
        raw_plate=inc.detected_plate or "",
        override_plate=payload.corrected_plate
    )
    inc.corrected_plate = validation["final_plate"]
    if payload.notes:
        inc.notes = (inc.notes or "") + f"\n[OCR Corrected to {inc.corrected_plate}]: {payload.notes}"

    db.commit()
    db.refresh(inc)
    return inc
