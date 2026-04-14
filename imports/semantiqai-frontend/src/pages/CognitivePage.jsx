import React from 'react'
import Card from '../components/Card'

export default function CognitivePage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Cognitive Lab</h2>
        <p className="muted">Memory, logic, focus, reasoning, and elite mental training modes.</p>
      </div>

      <div className="grid three-col">
        <Card title="Drill Console" desc="Logic drills, memory trials, speed rounds, and difficulty scaling." />
        <Card title="Profile Signals" desc="Cognitive profile metrics, consistency, streaks, and progress charts." />
        <Card title="Founder Elite Mode" desc="Reserved space for advanced founder cognition sessions and strategic drills." />
      </div>
    </div>
  )
}
