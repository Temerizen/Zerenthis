import React from 'react'
import Card from '../components/Card'

export default function ExecutionPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Execution Engine</h2>
        <p className="muted">Goals, plans, workflows, habits, and automation scaffolding.</p>
      </div>

      <div className="grid three-col">
        <Card title="Goal Planner" desc="Translate goals into actionable multi-step plans with priorities and risks." />
        <Card title="Task + Habit Rail" desc="Track execution momentum, routines, streaks, and completion scoring." />
        <Card title="Workflow Console" desc="Chain actions together for repeatable system behavior and automation prep." />
      </div>
    </div>
  )
}
