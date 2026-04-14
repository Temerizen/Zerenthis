"use client";

import { useState } from "react";
import { runAutopilot } from "@/lib/api";

type Props = {
  onRan?: () => void;
};

export default function RunAutopilot({ onRan }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRun = async () => {
    setLoading(true);
    const res = await runAutopilot();
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
      <h2 style={{ marginTop: 0 }}>Autopilot Control</h2>
      <p style={{ color: "#9ca3af", marginTop: 0 }}>
        Trigger the real backend autopilot route.
      </p>

      <button
        onClick={handleRun}
        disabled={loading}
        style={{
          padding: "10px 16px",
          background: loading ? "#374151" : "#2563eb",
          border: "none",
          borderRadius: "8px",
          color: "white",
          cursor: loading ? "default" : "pointer"
        }}
      >
        {loading ? "Running..." : "Run Autopilot"}
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
