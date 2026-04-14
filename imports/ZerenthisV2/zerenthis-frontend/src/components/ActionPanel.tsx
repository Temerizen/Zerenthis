"use client";

import { useState } from "react";
import {
  runPostingPlan,
  runPostingPrepare,
  runPostingExecute,
  getPostingResult,
  runRealityLoop,
  runRealityAutoLoop,
  runRealityExport,
  runScale,
  runTrafficReal,
  runTrafficBridge
} from "@/lib/api";

type Props = {
  onRan?: () => void;
};

export default function ActionPanel({ onRan }: Props) {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState("");

  const act = async (label: string, fn: () => Promise<any>) => {
    setLoading(label);
    const res = await fn();
    setResult({ action: label, response: res });
    setLoading("");
    onRan?.();
  };

  const buttonStyle: React.CSSProperties = {
    padding: "10px 12px",
    background: "#1f2937",
    border: "1px solid #374151",
    borderRadius: "8px",
    color: "white",
    cursor: "pointer"
  };

  return (
    <div style={{
      background: "#111827",
      padding: "16px",
      borderRadius: "14px",
      border: "1px solid #1f2937"
    }}>
      <h2 style={{ marginTop: 0 }}>Execution Actions</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
        <button style={buttonStyle} onClick={() => act("posting-plan", runPostingPlan)} disabled={!!loading}>Posting Plan</button>
        <button style={buttonStyle} onClick={() => act("posting-prepare", runPostingPrepare)} disabled={!!loading}>Posting Prepare</button>
        <button style={buttonStyle} onClick={() => act("posting-execute", runPostingExecute)} disabled={!!loading}>Posting Execute</button>
        <button style={buttonStyle} onClick={() => act("posting-result", getPostingResult)} disabled={!!loading}>Posting Result</button>
        <button style={buttonStyle} onClick={() => act("reality-loop", runRealityLoop)} disabled={!!loading}>Reality Loop</button>
        <button style={buttonStyle} onClick={() => act("reality-auto-loop", runRealityAutoLoop)} disabled={!!loading}>Reality Auto Loop</button>
        <button style={buttonStyle} onClick={() => act("reality-export", runRealityExport)} disabled={!!loading}>Reality Export</button>
        <button style={buttonStyle} onClick={() => act("scale-run", runScale)} disabled={!!loading}>Scale Run</button>
        <button style={buttonStyle} onClick={() => act("traffic-real", runTrafficReal)} disabled={!!loading}>Traffic Real</button>
        <button style={buttonStyle} onClick={() => act("traffic-bridge", runTrafficBridge)} disabled={!!loading}>Traffic Bridge</button>
      </div>

      {loading && <p style={{ color: "#9ca3af", marginTop: "12px" }}>Running {loading}...</p>}

      {result && (
        <pre style={{
          marginTop: "12px",
          fontSize: "11px",
          color: "#9ca3af",
          whiteSpace: "pre-wrap"
        }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
