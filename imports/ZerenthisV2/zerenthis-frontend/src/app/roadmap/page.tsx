export default function RoadmapPage() {
  const phases = [
    {
      title: "Phase 1 — Core Engine",
      status: "Complete",
      items: ["Backend API", "Basic Engines", "Execution Loop"]
    },
    {
      title: "Phase 2 — Automation + Evolution",
      status: "In Progress",
      items: ["Autopilot Loop", "Leaderboard", "Battle System", "Diversity Engine"]
    },
    {
      title: "Phase A — Control System",
      status: "Active",
      items: ["Frontend UI", "Navigation", "Control Panels"]
    },
    {
      title: "Phase B — Execution UI",
      status: "Upcoming",
      items: ["Live Logs", "Run Controls", "System Monitoring"]
    }
  ];

  return (
    <div>
      <h1 style={{ fontSize: "28px", marginBottom: "20px" }}>Zerenthis Roadmap</h1>

      {phases.map((phase, i) => (
        <div key={i} style={{
          background: "#111827",
          padding: "16px",
          borderRadius: "10px",
          marginBottom: "16px"
        }}>
          <h2>{phase.title}</h2>
          <p style={{ color: "#9ca3af" }}>{phase.status}</p>

          <ul>
            {phase.items.map((item, j) => (
              <li key={j}>• {item}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
