import React from 'react'
import Card from '../components/Card'

export default function SimulationPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Reality Simulation</h2>
        <p className="muted">Branching futures, strategic analysis, risk, opportunity, and command simulations.</p>
      </div>

      <div className="grid three-col">
        <Card title="Scenario Engine" desc="Context + decision inputs for short-term, mid-term, and long-term outcomes." />
        <Card title="Decision Tree" desc="Compare branches, consequences, leverage points, and optimal paths." />
        <Card title="Founder Command" desc="Reserved command simulation panels for high-level strategic planning." />
      </div>
    </div>
  )
}
