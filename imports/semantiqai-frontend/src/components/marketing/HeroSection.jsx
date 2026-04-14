import React from 'react'
import { Link } from 'react-router-dom'

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <div className="eyebrow">Intelligence infrastructure for ambitious humans</div>
        <h2>Learn faster. Think sharper. Execute harder. Create at scale.</h2>
        <p className="hero-text">
          SemantiqAI unifies cognitive training, AI education, execution systems,
          strategic simulation, creative production, and founder-grade control in one platform.
        </p>

        <div className="hero-actions">
          <Link to="/dashboard" className="primary-btn link-btn">Enter Platform</Link>
          <Link to="/pricing" className="ghost-btn link-btn">View Plans</Link>
        </div>
      </div>

      <div className="hero-panel">
        <div className="marketing-stack">
          <div className="pill">Cognitive Growth</div>
          <div className="pill">AI School</div>
          <div className="pill">Execution</div>
          <div className="pill">Simulation</div>
          <div className="pill">Creation</div>
          <div className="pill">Founder Control</div>
        </div>
      </div>
    </section>
  )
}
