"""
Rule-based detection engine.

Deliberately kept separate from the ML detector (anomaly.py): rules catch
known attack signatures deterministically and cheaply, while the ML layer
catches things nobody wrote a rule for yet. A real SOC runs both, and being
able to explain *why* is a good interview talking point.
"""
from collections import defaultdict
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.event import Event, Alert

# --- Tunable thresholds -----------------------------------------------------
BRUTE_FORCE_THRESHOLD = 5        # failed logins...
BRUTE_FORCE_WINDOW_MIN = 5       # ...within this many minutes -> alert

PORT_SCAN_THRESHOLD = 10         # distinct "denied/other" events from one IP...
PORT_SCAN_WINDOW_MIN = 2         # ...within this many minutes -> alert

OFF_HOURS_START = 0              # 00:00
OFF_HOURS_END = 5                # 05:00 — successful logins in this window are flagged


def detect_brute_force(db: Session) -> list[Alert]:
    """Flag source IPs with >= BRUTE_FORCE_THRESHOLD failed logins in a rolling window."""
    events = (
        db.query(Event)
        .filter(Event.event_type.in_(["login_failed", "login_invalid_user"]))
        .filter(Event.source_ip.isnot(None))
        .order_by(Event.timestamp)
        .all()
    )

    by_ip = defaultdict(list)
    for e in events:
        by_ip[e.source_ip].append(e)

    new_alerts = []
    for ip, ip_events in by_ip.items():
        ip_events.sort(key=lambda e: e.timestamp)
        window_start = 0
        for i in range(len(ip_events)):
            while (ip_events[i].timestamp - ip_events[window_start].timestamp) > timedelta(minutes=BRUTE_FORCE_WINDOW_MIN):
                window_start += 1
            count_in_window = i - window_start + 1
            if count_in_window >= BRUTE_FORCE_THRESHOLD:
                exists = (
                    db.query(Alert)
                    .filter(Alert.rule_name == "brute_force_ssh", Alert.source_ip == ip)
                    .first()
                )
                if not exists:
                    new_alerts.append(
                        Alert(
                            rule_name="brute_force_ssh",
                            severity="high",
                            source_ip=ip,
                            description=(
                                f"{count_in_window} failed SSH login attempts from {ip} "
                                f"within {BRUTE_FORCE_WINDOW_MIN} minutes."
                            ),
                            event_count=count_in_window,
                            detector="rule",
                        )
                    )
                break  # one alert per IP per run is enough for the demo
    return new_alerts


def detect_off_hours_login(db: Session) -> list[Alert]:
    """Flag successful logins between OFF_HOURS_START and OFF_HOURS_END local time."""
    events = db.query(Event).filter(Event.event_type == "login_success").all()

    new_alerts = []
    for e in events:
        if OFF_HOURS_START <= e.timestamp.hour < OFF_HOURS_END:
            exists = (
                db.query(Alert)
                .filter(
                    Alert.rule_name == "off_hours_login",
                    Alert.source_ip == e.source_ip,
                    Alert.description.like(f"%{e.user}%"),
                )
                .first()
            )
            if not exists:
                new_alerts.append(
                    Alert(
                        rule_name="off_hours_login",
                        severity="medium",
                        source_ip=e.source_ip,
                        description=(
                            f"Successful login for user '{e.user}' from {e.source_ip} "
                            f"at {e.timestamp.strftime('%H:%M')} (off-hours window)."
                        ),
                        event_count=1,
                        detector="rule",
                    )
                )
    return new_alerts


def run_all_rules(db: Session) -> list[Alert]:
    """Run every rule detector and persist any newly generated alerts."""
    alerts = []
    alerts.extend(detect_brute_force(db))
    alerts.extend(detect_off_hours_login(db))

    for a in alerts:
        db.add(a)
    db.commit()
    return alerts
