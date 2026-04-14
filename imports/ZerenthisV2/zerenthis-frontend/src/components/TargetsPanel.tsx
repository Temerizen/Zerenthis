"use client";

import { useEffect, useState } from "react";
import { getTargets } from "@/lib/api";

type Props = {
  refreshKey?: number;
};

function normalizeTargets(data: any): Array<{ name: string; score?: number }> {
  if (!data) return [];

  if (Array.isArray(data?.targets)) {
    return data.targets.map((t: any) => ({
      name: t.name || t.topic || t.target || "unknown_target",
      score: t.score,
    }));
  }

  if (Array.isArray(data?.ranked_targets)) {
    return data.ranked_targets.map((t: any) => ({
      name: t.name || t.topic || t.target || "unknown_target",
      score: t.score,
    }));
  }

  if (Array.isArray(data?.result?.ranked_targets)) {
    return data.result.ranked_targets.map((t: any) => ({
      name: t.name || t.topic || t.target || "unknown_target",
      score: t.score,
    }));
  }

  if (Array.isArray(data)) {
    return data.map((t: any) => ({
      name: t.name || t.topic || t.target || "unknown_target",
      score: t.score,
    }));
  }

  return [];
}

export default function TargetsPanel({ refreshKey = 0 }: Props) {
  const [data, setData] = useState<any>(null);
  const [targets, setTargets] = useState<Array<{ name: string; score?: number }>>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const res = await getTargets();
    setData(res);
    setTargets(normalizeTargets(res));
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [refreshKey]);

  return (
    <div style={{
      background: "#111827",
      padding: "16px",
      borderRadius: "14px",
      border: "1px solid #1f2937",
      minHeight: "220px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <h2 style={{ margin: 0 }}>Ranked Targets</h2>
        <button
          onClick={load}
          style={{
            padding: "8px 12px",
            background: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "white",
            cursor: "pointer"
          }}
        >
          Refresh
        </button>
      </div>

      {loading && <p style={{ color: "#9ca3af" }}>Ranking targets...</p>}

      {!loading && targets.length === 0 && (
        <pre style={{
          margin: 0,
          fontSize: "11px",
          color: "#9ca3af",
          whiteSpace: "pre-wrap"
        }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}

      {!loading && targets.length > 0 && (
        <div style={{ display: "grid", gap: "10px" }}>
          {targets.slice(0, 8).map((target, i) => (
            <div
              key={`${target.name}-${i}`}
              style={{
                background: "#0b1220",
                border: "1px solid #1f2937",
                borderRadius: "10px",
                padding: "10px 12px"
              }}
            >
              <div style={{ fontWeight: 600 }}>{target.name}</div>
              <div style={{ color: "#9ca3af", fontSize: "12px", marginTop: "4px" }}>
                Score: {target.score ?? "N/A"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
