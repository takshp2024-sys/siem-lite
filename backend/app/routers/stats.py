from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import Event, Alert
from app.schemas import StatsSummary

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def summary(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    alerts = db.query(Alert).all()

    severity_counts = Counter(a.severity for a in alerts)
    type_counts = Counter(e.event_type for e in events)
    ip_counts = Counter(e.source_ip for e in events if e.source_ip)

    top_ips = [{"source_ip": ip, "count": count} for ip, count in ip_counts.most_common(10)]

    return StatsSummary(
        total_events=len(events),
        total_alerts=len(alerts),
        alerts_by_severity=dict(severity_counts),
        events_by_type=dict(type_counts),
        top_source_ips=top_ips,
    )
