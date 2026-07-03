"""
Normalizes heterogeneous log formats into the common Event schema.

Currently supports:
  - Linux auth.log (SSH login attempts, sudo)
  - A generic JSON-lines format (for feeding synthetic/demo data or
    future Windows Event Log exports without changing the schema)

Design note: each parser is a pure function (text line -> dict | None).
Adding a new source is adding one function + one dispatch entry, not
touching ingestion or detection logic.
"""
import json
import re
from datetime import datetime
from typing import Optional

AUTH_LOG_PATTERN = re.compile(
    r"^(?P<month>\w{3})\s+(?P<day>\d+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+sshd\[\d+\]:\s+(?P<message>.+)$"
)

FAILED_PASSWORD = re.compile(
    r"Failed password for (invalid user )?(?P<user>\S+) from (?P<ip>[\d.]+) port \d+"
)
ACCEPTED_PASSWORD = re.compile(
    r"Accepted password for (?P<user>\S+) from (?P<ip>[\d.]+) port \d+"
)
INVALID_USER = re.compile(r"Invalid user (?P<user>\S+) from (?P<ip>[\d.]+)")


def _current_year() -> int:
    return datetime.now().year


def parse_auth_log_line(line: str) -> Optional[dict]:
    """Parse a single Linux /var/log/auth.log style line into a normalized event dict."""
    m = AUTH_LOG_PATTERN.match(line.strip())
    if not m:
        return None

    ts_str = f"{_current_year()} {m.group('month')} {m.group('day')} {m.group('time')}"
    try:
        timestamp = datetime.strptime(ts_str, "%Y %b %d %H:%M:%S")
    except ValueError:
        return None

    message = m.group("message")

    failed = FAILED_PASSWORD.search(message)
    if failed:
        return {
            "timestamp": timestamp,
            "source": "auth.log",
            "source_ip": failed.group("ip"),
            "user": failed.group("user"),
            "event_type": "login_failed",
            "severity": "low",
            "raw_message": message,
        }

    accepted = ACCEPTED_PASSWORD.search(message)
    if accepted:
        return {
            "timestamp": timestamp,
            "source": "auth.log",
            "source_ip": accepted.group("ip"),
            "user": accepted.group("user"),
            "event_type": "login_success",
            "severity": "info",
            "raw_message": message,
        }

    invalid = INVALID_USER.search(message)
    if invalid:
        return {
            "timestamp": timestamp,
            "source": "auth.log",
            "source_ip": invalid.group("ip"),
            "user": invalid.group("user"),
            "event_type": "login_invalid_user",
            "severity": "medium",
            "raw_message": message,
        }

    return {
        "timestamp": timestamp,
        "source": "auth.log",
        "source_ip": None,
        "user": None,
        "event_type": "other",
        "severity": "info",
        "raw_message": message,
    }


def parse_json_line(line: str) -> Optional[dict]:
    """Parse a JSON-lines event. Expects at minimum a timestamp + event_type."""
    line = line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    ts = data.get("timestamp")
    try:
        timestamp = datetime.fromisoformat(ts) if ts else datetime.now()
    except (ValueError, TypeError):
        timestamp = datetime.now()

    return {
        "timestamp": timestamp,
        "source": data.get("source", "json_feed"),
        "source_ip": data.get("source_ip"),
        "user": data.get("user"),
        "event_type": data.get("event_type", "other"),
        "severity": data.get("severity", "info"),
        "raw_message": data.get("raw_message", line),
    }


PARSERS = {
    "auth_log": parse_auth_log_line,
    "json": parse_json_line,
}


def parse_lines(lines: list[str], fmt: str) -> list[dict]:
    """Parse a batch of raw log lines using the named format. Skips unparseable lines."""
    parser = PARSERS.get(fmt)
    if not parser:
        raise ValueError(f"Unknown log format '{fmt}'. Supported: {list(PARSERS.keys())}")

    events = []
    for line in lines:
        parsed = parser(line)
        if parsed:
            events.append(parsed)
    return events
