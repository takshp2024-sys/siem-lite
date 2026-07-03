import { useEffect, useState } from "react";

export default function StatusBar({ totalEvents, totalAlerts, onRescan, scanning }) {
  const [clock, setClock] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "14px 24px",
        borderBottom: "1px solid var(--border)",
        background: "var(--surface)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: "var(--accent)",
            boxShadow: "0 0 8px var(--accent)",
          }}
        />
        <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, letterSpacing: 1 }}>
          SIEM-LITE
        </span>
        <span style={{ color: "var(--text-faint)", fontSize: 13 }}>SECURITY CONSOLE</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 28, fontFamily: "var(--font-mono)", fontSize: 13 }}>
        <Metric label="EVENTS" value={totalEvents} />
        <Metric label="ALERTS" value={totalAlerts} accent={totalAlerts > 0} />
        <button
          onClick={onRescan}
          disabled={scanning}
          style={{
            background: "transparent",
            border: "1px solid var(--border)",
            color: scanning ? "var(--text-faint)" : "var(--text)",
            padding: "6px 14px",
            borderRadius: 4,
            fontFamily: "var(--font-mono)",
            fontSize: 12,
            letterSpacing: 0.5,
          }}
        >
          {scanning ? "SCANNING…" : "RESCAN"}
        </button>
        <span style={{ color: "var(--text-faint)" }}>
          {clock.toLocaleTimeString("en-CA", { hour12: false })}
        </span>
      </div>
    </div>
  );
}

function Metric({ label, value, accent }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
      <span style={{ color: "var(--text-faint)", fontSize: 10, letterSpacing: 1 }}>{label}</span>
      <span style={{ color: accent ? "var(--accent)" : "var(--text)", fontWeight: 700 }}>
        {value}
      </span>
    </div>
  );
}
