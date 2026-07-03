from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.database import get_db
from app.models.event import Event, Alert
from app.schemas import EventOut, AlertOut

router = APIRouter(tags=["events"])


@router.get("/events", response_model=list[EventOut])
def list_events(
    db: Session = Depends(get_db),
    event_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    limit: int = Query(default=200, le=1000),
):
    q = db.query(Event)
    if event_type:
        q = q.filter(Event.event_type == event_type)
    if source_ip:
        q = q.filter(Event.source_ip == source_ip)
    return q.order_by(desc(Event.timestamp)).limit(limit).all()


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    severity: Optional[str] = None,
    detector: Optional[str] = None,
    limit: int = Query(default=200, le=1000),
):
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity)
    if detector:
        q = q.filter(Alert.detector == detector)
    return q.order_by(desc(Alert.created_at)).limit(limit).all()
