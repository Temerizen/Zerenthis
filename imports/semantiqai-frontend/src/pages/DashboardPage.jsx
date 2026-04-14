import React from "react"
import Card from "../components/Card"
import AIPanel from "../components/AIPanel"
import { useModules } from "../hooks/useModules"

function groupModules(modules) {
  const grouped = {}
  for (const mod of modules) {
    const group = mod.group || "general"
    if (!grouped[group]) grouped[group] = []
    grouped[group].push(mod)
  }
  return grouped
}

export default function DashboardPage() {
  const modules = useModules()
  const grouped = groupModules(modules)

  return (
    <div className="page">
      <div className="section-title">
        <h2>System Dashboard</h2>
        <p className="muted">Live module registry grouped by system domain.</p>
      </div>

      <AIPanel />

      {Object.keys(grouped).map((group) => (
        <section key={group} className="page">
          <div className="section-title">
            <h2>{group.charAt(0).toUpperCase() + group.slice(1)}</h2>
          </div>

          <div className="grid three-col">
            {grouped[group].map((mod) => (
              <Card
                key={mod.name}
                title={mod.name}
                desc={`Route: ${mod.route || "N/A"} • Blueprint: ${mod.blueprint || "Core module"}`}
                to={mod.route}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
