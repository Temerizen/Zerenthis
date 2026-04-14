"use client";

import { useState } from "react";
import { runAutonomyLoop } from "@/lib/api";

type Props = {
  onRan?: () => void;
};

export default function LoopControlPanel({ onRan }: Props) {
  const [iterations, setIterations] = useState(3);
  const [delay, setDelay] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runLoop = async () => {
    setLoading(true);
    const res = await runAutonomyLoop(iterations, delay);
    setResult(res);
    setLoading(false);
    onRan?.();
  };

  return (
    <div style={{
      background: "#111827",
      padding: "16px",
      borderRadius: "14px",
      border: "1px solid #1f2937"
    }}>
      <h2 style={{ marginTop: 0 }}>Loop Control</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "14px" }}>
        <div>
          <label style={{ display: "block", marginBottom: "6px", color: "#9ca3af" }}>Iterations</label>
          <input
            type="number"
            min="1"
            max="25"
            value={iterations}
            onChange={(e) => setIterations(Number(e.target.value))}
            style={{
              width: "100%",
              padding: "10px",
              background: "#0b1220",
              color: "white",
              border: "1px solid #374151",
              borderRadius: "8px"
            }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "6px", color: "#9ca3af" }}>Delay (sec)</label>
          <input
            type="number"
            min="0"
            max="60"
            value={delay}
            onChange={(e) => setDelay(Number(e.target.value))}
            style={{
              width: "100%",
              padding: "10px",
              background: "#0b1220",
              color: "white",
              border: "1px solid #374151",
              borderRadius: "8px"
            }}
          />
        </div>
      </div>

      <button
        onClick={runLoop}
        disabled={loading}
        style={{
          padding: "10px 16px",
          background: loading ? "#374151" : "#7c3aed",
          border: "none",
          borderRadius: "8px",
          color: "white",
          cursor: loading ? "default" : "pointer"
        }}
      >
        {loading ? "Running Loop..." : "Run Autonomy Loop"}
      </button>

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
