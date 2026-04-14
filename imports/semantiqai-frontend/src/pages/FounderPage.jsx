import React from 'react'
import Card from '../components/Card'
import FounderControlWidget from '../components/FounderControlWidget'

export default function FounderPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Founder Control Layer</h2>
        <p className="muted">Private command surfaces, logs, media controls, and strategic internal tooling.</p>
      </div>

      <div className="grid three-col">
        <Card title="Empire Snapshot" desc="Reserved surface for module health, state overview, and priority queue." />
        <Card title="Feature Toggles" desc="Reserved founder-only controls for internal module visibility and operation." />
        <Card title="Private Media Factory" desc="Reserved command area for script, thumbnail, video, and distribution flows." />
      </div>

      <div className="grid two-col">
        <FounderControlWidget />
        <Card title="Founder Notes + Logs" desc="Reserved surface for internal notes, maintenance mode, and action history." />
      </div>
    </div>
  )
}
