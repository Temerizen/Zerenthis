import React, { useState } from "react"
import { apiPost } from "../config/api"

export default function AIPanel() {
  const [input, setInput] = useState("")
  const [output, setOutput] = useState("")
  const [loading, setLoading] = useState(false)

  async function runAI() {
    const prompt = input.trim()
    if (!prompt) return

    setLoading(true)
    setOutput("")

    try {
      const data = await apiPost("/", { prompt })
      setOutput(data.response || "No response returned.")
    } catch (err) {
      setOutput(err.message || "Error connecting to backend.")
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      runAI()
    }
  }

  return (
    <section
      style={{
        marginTop: "24px",
        padding: "20px",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "18px",
        background: "rgba(12,18,40,0.72)"
      }}
    >
      <div style={{ marginBottom: "12px" }}>
        <h3 style={{ margin: 0, fontSize: "22px" }}>AI Command Center</h3>
        <p style={{ margin: "8px 0 0", opacity: 0.8 }}>
          Send a live prompt to the SemantiqAI backend.
        </p>
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask SemantiqAI anything..."
        rows={5}
        style={{
          width: "100%",
          padding: "14px",
          borderRadius: "14px",
          border: "1px solid rgba(255,255,255,0.1)",
          background: "#0c1430",
          color: "white",
          resize: "vertical",
          fontSize: "15px",
          outline: "none"
        }}
      />

      <div style={{ display: "flex", gap: "12px", marginTop: "12px", alignItems: "center" }}>
        <button
          onClick={runAI}
          disabled={loading}
          style={{
            padding: "12px 18px",
            borderRadius: "12px",
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
            background: "#8b7cff",
            color: "white",
            fontWeight: 700,
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? "Running..." : "Run AI"}
        </button>
      </div>

      <div
        style={{
          marginTop: "16px",
          minHeight: "120px",
          padding: "14px",
          borderRadius: "14px",
          background: "#0a1026",
          border: "1px solid rgba(255,255,255,0.08)",
          whiteSpace: "pre-wrap",
          lineHeight: 1.5
        }}
      >
        {output || "Response will appear here."}
      </div>
    </section>
  )
}
