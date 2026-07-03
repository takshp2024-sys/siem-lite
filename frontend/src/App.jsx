import { useEffect, useState, useCallback } from "react";
import StatusBar from "./components/StatusBar";
import AlertFeed from "./components/AlertFeed";
import IngestPanel from "./components/IngestPanel";
import { SeverityBreakdown, TopSourceIps, EventTypeBreakdown } from "./components/StatsPanels";
import { api } from "./lib/api";

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_events: 0,
    total_alerts: 0,
    alerts_by_severity: {},
    events_by_type: {},
    top_source_ips: [],
  });
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [alertsRes, statsRes] = await Promise.all([api.alerts(), api.stats()]);
      setAlerts(alertsRes);
      setStats(statsRes);
      setError(null);
    } catch (e) {
      setError("Cannot reach SIEM-lite API. Is the backend running on :8000?");
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 8000);
    return () => clearInterval(id);
  }, [refresh]);

  const handleRescan = async () => {
    setScanning(true);
    await api.rescan();
    await refresh();
    setScanning(false);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <StatusBar
        totalEvents={stats.total_events}
        totalAlerts={stats.total_alerts}
        onRescan={handleRescan}
        scanning={scanning}
      />

      {error && (
        <div style={{ background: "var(--sev-critical)", color: "#fff", padding: "8px 24px", fontSize: 13, fontFamily: "var(--font-mono)" }}>
          {error}
        </div>
      )}

      <div
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns: "380px 1fr",
          gap: 16,
          padding: 20,
          minHeight: 0,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
          <AlertFeed alerts={alerts} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto" }}>
          <IngestPanel onIngested={refresh} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <SeverityBreakdown alertsBySeverity={stats.alerts_by_severity} />
            <EventTypeBreakdown eventsByType={stats.events_by_type} />
          </div>
          <TopSourceIps topIps={stats.top_source_ips} />
        </div>
      </div>
    </div>
  );
}
