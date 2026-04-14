"use client";

import { useEffect, useState } from "react";

const base = "http://127.0.0.1:8000/api";

export default function FounderMarket() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const headers = {
    "x-api-key": "ZERENTHIS_FOUNDER_KEY",
    "Content-Type": "application/json"
  };

  const runCycle = async () => {
    setLoading(true);
    try {
      const res = await fetch(base + "/founder/market/run", {
        method: "POST",
        headers
      });
      const json = await res.json();
      setData(json);
    } finally {
      setLoading(false);
    }
  };

  const resetPortfolio = async () => {
    setLoading(true);
    try {
      await fetch(base + "/founder/market/reset-portfolio", {
        method: "POST",
        headers,
        body: JSON.stringify({
          starting_balance: 50,
          risk_per_trade: 0.1
        })
      });
      await runCycle();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCycle();
  }, []);

  if (!data) {
    return (
      <div style={{ padding: 24, background: "#05070d", color: "white", minHeight: "100vh" }}>
        Loading founder terminal...
      </div>
    );
  }

  const { portfolio, score, scan, signals, trades } = data;

  const buttonStyle: React.CSSProperties = {
    background: "#06b6d4",
    color: "#001018",
    border: "none",
    borderRadius: 10,
    padding: "12px 18px",
    fontWeight: 700,
    fontSize: 14,
    cursor: "pointer",
    minWidth: 140
  };

  return (
    <div
      style={{
        padding: 24,
        fontFamily: "monospace",
        background: "#05070d",
        color: "#00e5ff",
        minHeight: "100vh"
      }}
    >
      <h1 style={{ color: "white", marginBottom: 20 }}>🚀 Zerenthis Founder Terminal</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
        <button onClick={runCycle} disabled={loading} style={buttonStyle}>
          {loading ? "Running..." : "Run Cycle"}
        </button>

        <button
          onClick={resetPortfolio}
          disabled={loading}
          style={{ ...buttonStyle, background: "#f59e0b", color: "#1a1200" }}
        >
          Reset $50
        </button>
      </div>

      <div style={{ display: "flex", gap: 20, marginBottom: 24, flexWrap: "wrap", color: "white" }}>
        <div>💰 Balance: ${portfolio?.balance?.toFixed?.(2) ?? "0.00"}</div>
        <div>📈 PnL: {score?.pnl_percent ?? 0}%</div>
        <div>⚔️ Trades: {score?.trades ?? 0}</div>
      </div>

      <h2 style={{ color: "white" }}>📊 Market</h2>
      <table style={{ width: "100%", marginBottom: 24, color: "white" }}>
        <thead>
          <tr>
            <th align="left">Asset</th>
            <th align="left">Price</th>
            <th align="left">% Change</th>
            <th align="left">Signal</th>
            <th align="left">Reason</th>
          </tr>
        </thead>
        <tbody>
          {(scan || []).map((item: any) => {
            const signal = (signals || []).find((s: any) => s.asset === item.asset);
            return (
              <tr key={item.asset}>
                <td>{item.asset}</td>
                <td>${item.price}</td>
                <td style={{ color: item.change >= 0 ? "#22c55e" : "#ef4444" }}>{item.change}%</td>
                <td>{signal?.action || "-"}</td>
                <td>{signal?.reason || "-"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <h2 style={{ color: "white" }}>⚔️ Trades</h2>
      <table style={{ width: "100%", color: "white" }}>
        <thead>
          <tr>
            <th align="left">Asset</th>
            <th align="left">Action</th>
            <th align="left">Size</th>
            <th align="left">Profit</th>
            <th align="left">Balance</th>
          </tr>
        </thead>
        <tbody>
          {(trades || []).map((t: any, i: number) => (
            <tr key={i}>
              <td>{t.asset}</td>
              <td>{t.action}</td>
              <td>${t.position_size}</td>
              <td style={{ color: t.profit >= 0 ? "#22c55e" : "#ef4444" }}>{t.profit}</td>
              <td>${t.account_balance}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}