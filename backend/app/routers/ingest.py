from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.log_parser import parse_lines
from app.models.event import Event
from app.detection.rules import run_all_rules
from app.detection.anomaly import run_isolation_forest

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/text")
def ingest_text(payload: dict, db: Session = Depends(get_db)):
    """
    Ingest raw log lines directly (JSON body: {"format": "auth_log", "lines": [...]})
    Runs detection immediately after ingest so the demo feels real-time.
    """
    fmt = payload.get("format")
    lines = payload.get("lines", [])
    if not fmt or not lines:
        raise HTTPException(400, "Both 'format' and 'lines' are required.")

    try:
        parsed = parse_lines(lines, fmt)
    except ValueError as e:
        raise HTTPException(400, str(e))

    for p in parsed:
        db.add(Event(**p))
    db.commit()

    rule_alerts = run_all_rules(db)
    ml_alerts = run_isolation_forest(db)

    return {
        "events_ingested": len(parsed),
        "new_rule_alerts": len(rule_alerts),
        "new_ml_alerts": len(ml_alerts),
    }


@router.post("/file")
async def ingest_file(fmt: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Ingest a log file upload (e.g. an auth.log export)."""
    raw = await file.read()
    # Windows tools (notably PowerShell's `>` redirection) commonly write
    # UTF-16 instead of UTF-8. Detect the BOM and decode correctly rather
    # than silently mangling every line with errors="ignore".
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        content = raw.decode("utf-16")
    else:
        content = raw.decode("utf-8", errors="ignore")
    lines = content.splitlines()

    try:
        parsed = parse_lines(lines, fmt)
    except ValueError as e:
        raise HTTPException(400, str(e))

    for p in parsed:
        db.add(Event(**p))
    db.commit()

    rule_alerts = run_all_rules(db)
    ml_alerts = run_isolation_forest(db)

    return {
        "events_ingested": len(parsed),
        "new_rule_alerts": len(rule_alerts),
        "new_ml_alerts": len(ml_alerts),
    }


@router.post("/rescan")
def rescan(db: Session = Depends(get_db)):
    """Re-run detection over all currently stored events without ingesting new data."""
    rule_alerts = run_all_rules(db)
    ml_alerts = run_isolation_forest(db)
    return {"new_rule_alerts": len(rule_alerts), "new_ml_alerts": len(ml_alerts)}