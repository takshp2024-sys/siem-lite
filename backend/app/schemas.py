from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    source: str
    source_ip: Optional[str] = None
    user: Optional[str] = None
    event_type: str
    severity: str
    raw_message: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    rule_name: str
    severity: str
    source_ip: Optional[str] = None
    description: str
    event_count: int
    detector: str
    score: Optional[float] = None


class IngestPayload(BaseModel):
    format: str          # "auth_log" | "json"
    lines: list[str]


class StatsSummary(BaseModel):
    total_events: int
    total_alerts: int
    alerts_by_severity: dict[str, int]
    events_by_type: dict[str, int]
    top_source_ips: list[dict]
