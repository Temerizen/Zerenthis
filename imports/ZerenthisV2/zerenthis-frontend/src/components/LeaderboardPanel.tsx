"use client";

import { useEffect, useState } from "react";
import { getLeaderboard } from "@/lib/api";

type Props = {
  refreshKey?: number;
};

function normalizeLeaderboard(data: any): Array<{ name: string; score?: number; revenue?: number; conversions?: number }> {
  if (!data) return [];

  if (Array.isArray(data)) {
    return data.map((x: any) => ({
      name: x.topic || x.name || x.target || "unknown",
      score: x.score,
      revenue: x.revenue,
      conversions: x.conversions,
    }));
  }

  if (Array.isArray(data?.entries)) {
    return data.entries.map((x: any) => ({
      name: x.topic || x.name || x.target || "unknown",
      score: x.score,
      revenue: x.revenue,
      conversions: x.conversions,
    }));
  }

  if (typeof data === "object") {
    return Object.entries(data).map(([key, val]: any) => ({
      name: key,
      score: val?.score,
      revenue: val?.revenue,
      conversions: val?.conversions,
    }));
  }

  return [];
}

export default function LeaderboardPanel({ refreshKey = 0 }: Props) {
  const [rows, setRows] = useState<Array<{ name: string; score?: number; revenue?: number; conversions?: number }>>([]);
  const [raw, setRaw] = useState<any>(null);

  const load = async () => {
    const res = await getLeaderboard();
    setRaw(res);
    setRows(normalizeLeaderboard(res));
  };

  useEffect(() => {
    load();
  }, [refreshKey]);

  return (
    <div style={{
      background: "#111827",
      padding: "16px",
      borderRadius: "14px",
      border: "1px solid #1f2937"
    }}>
      <h2 style={{ marginTop: 0 }}>Leaderboard</h2>

      {rows.length === 0 ? (
        <pre style={{
          marginTop: "8px",
          fontSize: "11px",
          color: "#9ca3af",
          whiteSpace: "pre-wrap"
        }}>
          {JSON.stringify(raw, null, 2)}
        </pre>
      ) : (
        <div style={{ display: "grid", gap: "10px" }}>
          {rows.slice(0, 8).map((row, i) => (
            <div
              key={`${row.name}-${i}`}
              style={{
                background: "#0b1220",
                border: "1px solid #1f2937",
                borderRadius: "10px",
                padding: "10px 12px"
              }}
            >
              <div style={{ fontWeight: 600 }}>{row.name}</div>
              <div style={{ fontSize: "12px", color: "#9ca3af", marginTop: "4px" }}>
                Score: {row.score ?? "N/A"} • Revenue: {row.revenue ?? 0} • Conversions: {row.conversions ?? 0}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
