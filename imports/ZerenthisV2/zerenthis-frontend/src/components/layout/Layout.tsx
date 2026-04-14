"use client";

import Link from "next/link";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", height: "100vh", background: "#0b0f19", color: "white" }}>
      
      {/* SIDEBAR */}
      <div style={{
        width: "240px",
        background: "#111827",
        padding: "20px",
        borderRight: "1px solid #1f2937"
      }}>
        <h2 style={{ marginBottom: "20px" }}>Zerenthis</h2>

        {[
          ["Dashboard", "/dashboard"],
          ["Roadmap", "/roadmap"],
          ["Systems", "/systems"],
          ["Money", "/money"],
          ["Traffic", "/traffic"],
          ["Leaderboard", "/leaderboard"],
          ["Lab", "/lab"]
        ].map(([name, path]) => (
          <div key={path} style={{ marginBottom: "12px" }}>
            <Link href={path} style={{ color: "#9ca3af", textDecoration: "none" }}>
              {name}
            </Link>
          </div>
        ))}
      </div>

      {/* MAIN CONTENT */}
      <div style={{ flex: 1, padding: "24px", overflowY: "auto" }}>
        {children}
      </div>
    </div>
  );
}
