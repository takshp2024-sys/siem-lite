import { SEVERITY_COLOR } from "../lib/api";

const DETECTOR_LABEL = { rule: "RULE", ml: "ML · ISOLATION FOREST" };

export default function AlertFeed({ alerts }) {
  return (
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        display: "flex",
        flexDirection: "column",
        minHeight: 0,
      }}
    >
      <div
        style={{
          padding: "14px 18px",
          borderBottom: "1px solid var(--border)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, letterSpacing: 1, color: "var(--text-muted)" }}>
          ALERT FEED
        </span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-faint)" }}>
          {alerts.length} ACTIVE
        </span>
      </div>

      <div style={{ overflowY: "auto", flex: 1 }}>
        {alerts.length === 0 && (
          <div style={{ padding: 24, color: "var(--text-faint)", fontSize: 13, textAlign: "center" }}>
            No alerts. Ingest logs or run a rescan to populate the feed.
          </div>
        )}

        {alerts.map((a) => (
          <div
            key={a.id}
            style={{
              padding: "12px 18px",
              borderBottom: "1px solid var(--border)",
              borderLeft: `3px solid ${SEVERITY_COLOR[a.severity] || "var(--sev-info)"}`,
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 11,
                  fontWeight: 700,
                  letterSpacing: 0.5,
                  color: SEVERITY_COLOR[a.severity],
                  textTransform: "uppercase",
                }}
              >
                {a.severity} · {a.rule_name.replace(/_/g, " ")}
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-faint)" }}>
                {DETECTOR_LABEL[a.detector] || a.detector}
              </span>
            </div>
            <div style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.4 }}>{a.description}</div>
            <div style={{ fontSize: 11, color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}>
              {a.source_ip && `src: ${a.source_ip}  ·  `}
              {new Date(a.created_at).toLocaleString("en-CA", { hour12: false })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
