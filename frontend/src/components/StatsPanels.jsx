import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";
import { SEVERITY_COLOR } from "../lib/api";

const PANEL_STYLE = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  padding: "14px 18px",
};

const TITLE_STYLE = {
  fontFamily: "var(--font-mono)",
  fontSize: 13,
  letterSpacing: 1,
  color: "var(--text-muted)",
  marginBottom: 12,
};

export function SeverityBreakdown({ alertsBySeverity }) {
  const order = ["critical", "high", "medium", "low", "info"];
  const data = order
    .filter((s) => alertsBySeverity[s])
    .map((s) => ({ severity: s, count: alertsBySeverity[s] }));

  return (
    <div style={PANEL_STYLE}>
      <div style={TITLE_STYLE}>ALERTS BY SEVERITY</div>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
          <XAxis type="number" tick={{ fill: "var(--text-faint)", fontSize: 11 }} stroke="var(--border)" allowDecimals={false} />
          <YAxis
            type="category"
            dataKey="severity"
            tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            stroke="var(--border)"
            width={70}
          />
          <Tooltip
            contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)", fontSize: 12 }}
            labelStyle={{ color: "var(--text)" }}
          />
          <Bar dataKey="count" radius={[0, 3, 3, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={SEVERITY_COLOR[d.severity]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TopSourceIps({ topIps }) {
  return (
    <div style={PANEL_STYLE}>
      <div style={TITLE_STYLE}>TOP SOURCE IPS</div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={topIps} margin={{ left: -10, right: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="source_ip"
            tick={{ fill: "var(--text-faint)", fontSize: 10, fontFamily: "var(--font-mono)" }}
            stroke="var(--border)"
            angle={-35}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fill: "var(--text-faint)", fontSize: 11 }} stroke="var(--border)" allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)", fontSize: 12 }}
            labelStyle={{ color: "var(--text)" }}
          />
          <Bar dataKey="count" fill="var(--accent)" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function EventTypeBreakdown({ eventsByType }) {
  const data = Object.entries(eventsByType)
    .map(([type, count]) => ({ type, count }))
    .sort((a, b) => b.count - a.count);

  return (
    <div style={PANEL_STYLE}>
      <div style={TITLE_STYLE}>EVENTS BY TYPE</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {data.map((d) => (
          <div key={d.type} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span
              style={{
                width: 130,
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                color: "var(--text-muted)",
                flexShrink: 0,
              }}
            >
              {d.type}
            </span>
            <div style={{ flex: 1, background: "var(--surface-raised)", borderRadius: 3, height: 8, overflow: "hidden" }}>
              <div
                style={{
                  width: `${(d.count / data[0].count) * 100}%`,
                  background: "var(--accent-dim)",
                  height: "100%",
                }}
              />
            </div>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-faint)", width: 30, textAlign: "right" }}>
              {d.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
