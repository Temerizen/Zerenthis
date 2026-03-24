"use client";

import { useState } from "react";

export default function Page() {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("product");
  const [feedback, setFeedback] = useState("");

  const generate = async () => {
    if (!idea) return;

    setLoading(true);

    try {
      const res = await fetch("/api/generate-fast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#05070d",
        color: "white",
        padding: 20,
      }}
    >
      <h1 style={{ color: "#00e5ff" }}>Zerenthis Studio ⚡</h1>

      {/* INPUT */}
      <input
        placeholder="Enter topic..."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        style={{
          width: "100%",
          padding: 14,
          marginTop: 20,
          borderRadius: 10,
          border: "none",
          background: "#111",
          color: "white",
        }}
      />

      {/* GENERATE BUTTON */}
      <button
        onClick={generate}
        style={{
          marginTop: 20,
          padding: "12px 20px",
          background: "#00e5ff",
          border: "none",
          borderRadius: 10,
          fontWeight: "bold",
          cursor: "pointer",
        }}
      >
        {loading ? "Generating..." : "Generate Product"}
      </button>

      {/* RESULTS */}
      {result && (
        <div style={{ marginTop: 30 }}>
          {/* TABS */}
          <div style={{ display: "flex", gap: 10 }}>
            <button onClick={() => setActiveTab("product")}>
              📄 Product
            </button>
            <button onClick={() => setActiveTab("youtube")}>
              🎬 YouTube
            </button>
            <button onClick={() => setActiveTab("shorts")}>
              ⚡ Shorts
            </button>
          </div>

          {/* OUTPUT */}
          <div
            style={{
              marginTop: 20,
              padding: 20,
              background: "#0a0a0a",
              borderRadius: 10,
              whiteSpace: "pre-wrap",
            }}
          >
            {result[activeTab]}
          </div>

          {/* DIRECTOR CHAT */}
          <textarea
            placeholder="Tell AI what to improve..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            style={{
              width: "100%",
              marginTop: 20,
              padding: 12,
              borderRadius: 10,
              background: "#111",
              color: "white",
            }}
          />

          <button
            style={{
              marginTop: 10,
              padding: "10px 16px",
              background: "#222",
              color: "white",
              borderRadius: 8,
              cursor: "pointer",
            }}
          >
            Apply Changes
          </button>
        </div>
      )}
    </main>
  );
}