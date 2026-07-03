const BASE = "/api";

async function getJson(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export const api = {
  alerts: (params = "") => getJson(`/alerts${params}`),
  events: (params = "") => getJson(`/events${params}`),
  stats: () => getJson(`/stats/summary`),
  rescan: () =>
    fetch(`${BASE}/ingest/rescan`, { method: "POST" }).then((r) => r.json()),
  ingestText: (format, lines) =>
    fetch(`${BASE}/ingest/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format, lines }),
    }).then((r) => r.json()),
};

export const SEVERITY_COLOR = {
  info: "var(--sev-info)",
  low: "var(--sev-low)",
  medium: "var(--sev-medium)",
  high: "var(--sev-high)",
  critical: "var(--sev-critical)",
};
