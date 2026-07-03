"""
Core data model.

Event  = a single normalized log line, regardless of original source format
Alert  = something the detection engine (rules or ML) flagged about one
         or more events
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    source = Column(String(64), index=True)          # e.g. "auth.log", "windows_security"
    source_ip = Column(String(64), index=True, nullable=True)
    user = Column(String(128), nullable=True)
    event_type = Column(String(64), index=True)       # e.g. "login_failed", "login_success", "port_scan"
    severity = Column(String(16), default="info")     # info | low | medium | high | critical
    raw_message = Column(Text)
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rule_name = Column(String(128), index=True)        # e.g. "brute_force_ssh", "isolation_forest_outlier"
    severity = Column(String(16), default="medium")
    source_ip = Column(String(64), index=True, nullable=True)
    description = Column(Text)
    event_count = Column(Integer, default=1)
    detector = Column(String(32), default="rule")       # "rule" | "ml"
    score = Column(Float, nullable=True)                 # anomaly score, if ML-generated
