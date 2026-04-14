"use client";

import { useEffect, useState } from "react";
import { getHealth, getPhaseVerify } from "@/lib/api";

type Props = {
  refreshKey?: number;
};

export default function SystemStatusPanel({ refreshKey = 0 }: Props) {
  const [health, setHealth] = useState<any>(null);
  const [phase, setPhase] = useState<any>(null);

  const load = async () => {
    const [h, p] = await Promise.all([
      getHealth(),
      getPhaseVerify(),
    ]);
    setHealth(h);
    setPhase(p);
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
      <h2 style={{ marginTop: 0 }}>System Status</h2>

      <div style={{ display: "grid", gap: "10px" }}>
        <div style={{
          background: "#0b1220",
          borderRadius: "10px",
          padding: "10px 12px",
          border: "1px solid #1f2937"
        }}>
          <div style={{ fontSize: "12px", color: "#9ca3af" }}>Backend</div>
          <div style={{ color: health?.status === "ok" ? "#10b981" : "#ef4444", fontWeight: 700, marginTop: "4px" }}>
            {health?.status || "unknown"}
          </div>
        </div>

        <div style={{
          background: "#0b1220",
          borderRadius: "10px",
          padding: "10px 12px",
          border: "1px solid #1f2937"
        }}>
          <div style={{ fontSize: "12px", color: "#9ca3af" }}>Phase Verification</div>
          <div style={{ color: "#e5e7eb", marginTop: "4px", whiteSpace: "pre-wrap" }}>
            {phase?.status || phase?.phase || phase?.message || JSON.stringify(phase)}
          </div>
        </div>
      </div>
    </div>
  );
}
