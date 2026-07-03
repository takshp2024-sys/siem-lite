# Architecture Notes

This is the expanded version of the README's Mermaid diagram — useful if you're
prepping to explain the system in an interview, or want prose to adapt into
slides.

## 1. Ingestion

Two entry points, both landing in the same normalization step:

- `POST /ingest/file` — upload a raw log file (e.g. an `auth.log` export)
- `POST /ingest/text` — push raw lines directly in a JSON body (used by the
  dashboard's manual ingest panel, and the easiest path for a demo)

Both call `log_parser.parse_lines()`, which dispatches to a format-specific
parser (`auth_log` or `json`). Adding a new source — say, Windows Event Log
exports or a cloud provider's audit log — means writing one new parser
function that returns the same normalized dict shape. Nothing downstream
needs to change.

## 2. Normalization (the Event schema)

Every parser produces the same shape regardless of source:

```
timestamp, source, source_ip, user, event_type, severity, raw_message
```

This is the core design decision that makes multi-source detection possible:
the rule engine and the ML model both operate on `Event` rows without caring
whether the data originally came from `auth.log` or a JSON feed.

## 3. Detection

Runs automatically after every ingest, and can also be triggered manually via
`POST /ingest/rescan` (useful after adjusting thresholds, or to re-score
historical data with a freshly retrained model).

**Rule engine** (`detection/rules.py`) — deterministic, signature-based:
- Sliding window brute-force detection (per source IP)
- Off-hours login flagging

**ML engine** (`detection/anomaly.py`) — behavioral, unsupervised:
- Aggregates events into a per-IP feature vector
- Fits Isolation Forest fresh on each run (demo-scale simplicity; a
  production version would persist the trained model and score new events
  against it incrementally rather than refitting from scratch)
- Flags statistical outliers regardless of whether they match a known
  signature

Alerts from both engines write to the same `Alert` table, distinguished by a
`detector` field (`rule` vs `ml`), so the dashboard can display both in one
unified feed while still letting you filter by detector type.

## 4. Presentation

The dashboard polls `/alerts` and `/stats/summary` every 8 seconds. This is
intentionally simple polling rather than WebSockets — appropriate for a
portfolio-scale demo, and an easy, well-scoped upgrade to mention if asked
"how would you make this real-time" in an interview (swap polling for a
WebSocket push from the backend on new alert creation).

## Where this maps to real SOC tooling

| This project | Real-world equivalent |
|---|---|
| `log_parser.py` | Filebeat / Logstash / Fluentd parsing pipelines |
| `Event` table | Normalized index in Elasticsearch / Splunk |
| Rule engine | Suricata/Snort signatures, Sigma rules |
| Isolation Forest | UEBA (User and Entity Behavior Analytics) layer |
| React dashboard | Kibana / Splunk dashboards / Wazuh UI |

Naming this mapping explicitly in an interview is usually more valuable than
the code itself — it shows you understand *why* each piece exists, not just
that you can build a CRUD app with a chart on top.
