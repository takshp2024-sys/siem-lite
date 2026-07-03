"""
Statistical anomaly detection using Isolation Forest.

This is the differentiator vs. a plain rules-only SIEM: it catches
behavioral outliers (unusual login timing/frequency per source IP) that
don't match a predefined signature. Same modeling approach as the
Robot Sensor Anomaly Detector (LSTM Autoencoder + Isolation Forest),
adapted here to per-IP login behavior features.

Features per source IP, over the whole ingested window:
  - total event count
  - failed-login ratio
  - distinct users attempted
  - mean seconds between events (bursty vs. spread out)
  - std-dev of event hour-of-day (spread across the day vs. clustered)
"""
from datetime import datetime
from collections import defaultdict

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.models.event import Event, Alert

MIN_EVENTS_FOR_ML = 20   # not enough data below this -> skip ML pass entirely
CONTAMINATION = 0.1       # assume ~10% of source IPs are anomalous, tune per environment


def _build_ip_features(db: Session):
    events = db.query(Event).filter(Event.source_ip.isnot(None)).all()
    if len(events) < MIN_EVENTS_FOR_ML:
        return [], None

    by_ip = defaultdict(list)
    for e in events:
        by_ip[e.source_ip].append(e)

    ips, rows = [], []
    for ip, evs in by_ip.items():
        evs.sort(key=lambda e: e.timestamp)
        total = len(evs)
        failed = sum(1 for e in evs if e.event_type in ("login_failed", "login_invalid_user"))
        distinct_users = len({e.user for e in evs if e.user})
        hours = [e.timestamp.hour for e in evs]

        if total > 1:
            deltas = [
                (evs[i + 1].timestamp - evs[i].timestamp).total_seconds()
                for i in range(total - 1)
            ]
            mean_gap = float(np.mean(deltas))
        else:
            mean_gap = 0.0

        hour_std = float(np.std(hours)) if len(hours) > 1 else 0.0

        ips.append(ip)
        rows.append([total, failed / total, distinct_users, mean_gap, hour_std])

    return ips, np.array(rows)


def run_isolation_forest(db: Session) -> list[Alert]:
    """Score each source IP's behavior; flag outliers as ML-detected alerts."""
    ips, X = _build_ip_features(db)
    if not ips:
        return []

    model = IsolationForest(contamination=CONTAMINATION, random_state=42, n_estimators=200)
    model.fit(X)
    scores = model.decision_function(X)     # lower = more anomalous
    predictions = model.predict(X)           # -1 = outlier, 1 = normal

    new_alerts = []
    for ip, score, pred in zip(ips, scores, predictions):
        if pred == -1:
            exists = (
                db.query(Alert)
                .filter(Alert.rule_name == "isolation_forest_outlier", Alert.source_ip == ip)
                .first()
            )
            if not exists:
                new_alerts.append(
                    Alert(
                        rule_name="isolation_forest_outlier",
                        severity="medium",
                        source_ip=ip,
                        description=(
                            f"Source IP {ip} flagged as a behavioral outlier "
                            f"(anomaly score {score:.3f}) based on login frequency, "
                            f"failure ratio, and timing pattern."
                        ),
                        event_count=1,
                        detector="ml",
                        score=float(score),
                    )
                )

    for a in new_alerts:
        db.add(a)
    db.commit()
    return new_alerts
