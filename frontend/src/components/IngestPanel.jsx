import { useState } from "react";
import { api } from "../lib/api";

export default function IngestPanel({ onIngested }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const handleIngest = async () => {
    if (!text.trim()) return;
    setBusy(true);
    setResult(null);
    try {
      const lines = text.split("\n").filter((l) => l.trim());
      const res = await api.ingestText("auth_log", lines);
      setResult(res);
      setText("");
      onIngested();
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        padding: "14px 18px",
      }}
    >
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 13, letterSpacing: 1, color: "var(--text-muted)", marginBottom: 10 }}>
        INGEST LOG LINES (auth.log format)
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste raw auth.log lines here, one per line…"
        rows={4}
        style={{
          width: "100%",
          background: "var(--bg)",
          border: "1px solid var(--border)",
          borderRadius: 4,
          color: "var(--text)",
          fontFamily: "var(--font-mono)",
          fontSize: 12,
          padding: 10,
          resize: "vertical",
        }}
      />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 10 }}>
        <span style={{ fontSize: 11, color: "var(--text-faint)" }}>
          {result && !result.error && `Ingested ${result.events_ingested} events · ${result.new_rule_alerts + result.new_ml_alerts} new alerts`}
          {result?.error && <span style={{ color: "var(--sev-critical)" }}>{result.error}</span>}
        </span>
        <button
          onClick={handleIngest}
          disabled={busy}
          style={{
            background: "var(--accent-dim)",
            border: "none",
            color: "#1a1a1a",
            fontWeight: 700,
            padding: "8px 18px",
            borderRadius: 4,
            fontFamily: "var(--font-mono)",
            fontSize: 12,
          }}
        >
          {busy ? "INGESTING…" : "INGEST"}
        </button>
      </div>
    </div>
  );
}
