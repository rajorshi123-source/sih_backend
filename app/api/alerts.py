from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Alert
from app.schemas.schemas import AlertResponse, AlertAcknowledge

router = APIRouter(prefix="/alerts", tags=["Urban Safety Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_all_alerts(
    severity: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == is_acknowledged)

    return query.order_by(Alert.timestamp.desc()).all()

@router.get("/unread-count")
def get_unread_alerts_count(db: Session = Depends(get_db)):
    unread = db.query(Alert).filter(Alert.is_read == False).count()
    unacknowledged = db.query(Alert).filter(Alert.is_acknowledged == False).count()
    critical = db.query(Alert).filter(Alert.severity == "CRITICAL", Alert.is_acknowledged == False).count()
    return {
        "unread_count": unread,
        "unacknowledged_count": unacknowledged,
        "critical_count": critical
    }

@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, payload: AlertAcknowledge, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter((Alert.id == alert_id) | (Alert.alert_code == alert_id)).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_acknowledged = True
    alert.is_read = True
    alert.acknowledged_by = payload.acknowledged_by
    db.commit()
    db.refresh(alert)
    return alert

@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter((Alert.id == alert_id) | (Alert.alert_code == alert_id)).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    alert.is_acknowledged = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert
