import React from "react"
import { Link } from "react-router-dom"
import Header from "../components/Header"

const pillars = [
  {
    title: "Learn",
    text: "Study any subject with structured AI tutoring, guided tracks, and deep understanding loops.",
    href: "/school"
  },
  {
    title: "Execute",
    text: "Turn goals into plans, tasks, momentum, and clear next actions without getting buried.",
    href: "/execution"
  },
  {
    title: "Create",
    text: "Generate ideas, drafts, systems, and polished outputs from one command center.",
    href: "/creation"
  }
]

const highlights = [
  "AI School for any subject",
  "Cognitive Lab for sharper thinking",
  "Execution Engine for real action",
  "Reality Simulation for scenario planning",
  "Infinite Creation for output generation",
  "Founder Control for private system oversight"
]

export default function HomePage() {
  return (
    <div className="marketing-shell">
      <Header />

      <main className="marketing-page">
        <section className="hero-section">
          <div className="hero-copy">
            <div className="eyebrow">SEMANTIQAI ASCENSION</div>
            <h1>Turn thought into execution.</h1>
            <p className="hero-text">
              SemantiqAI is an intelligence workspace for learning, planning,
              creating, and operating at a higher level without juggling ten
              disconnected tools.
            </p>

            <div className="hero-actions">
              <Link to="/dashboard" className="primary-btn link-btn">
                Open App
              </Link>
              <a href="#capabilities" className="ghost-btn link-btn">
                See Capabilities
              </a>
            </div>

            <div className="hero-proof">
              <span className="proof-pill">Learn faster</span>
              <span className="proof-pill">Execute clearly</span>
              <span className="proof-pill">Create at scale</span>
            </div>
          </div>

          <div className="hero-visual card">
            <div className="hero-visual-top">
              <span className="status-dot live" />
              <span>System online</span>
            </div>

            <div className="hero-metrics">
              <div className="metric-card">
                <div className="metric-label">Modules</div>
                <div className="metric-value">6</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Mode</div>
                <div className="metric-value">Founder</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Focus</div>
                <div className="metric-value">Live</div>
              </div>
            </div>

            <div className="hero-stack">
              <div className="stack-row">
                <span>AI School</span>
                <span className="stack-tag">Ready</span>
              </div>
              <div className="stack-row">
                <span>Cognitive Lab</span>
                <span className="stack-tag">Ready</span>
              </div>
              <div className="stack-row">
                <span>Execution Engine</span>
                <span className="stack-tag">Ready</span>
              </div>
              <div className="stack-row">
                <span>Reality Simulation</span>
                <span className="stack-tag">Ready</span>
              </div>
              <div className="stack-row">
                <span>Infinite Creation</span>
                <span className="stack-tag">Ready</span>
              </div>
              <div className="stack-row">
                <span>Founder Control</span>
                <span className="stack-tag founder-tag">Private</span>
              </div>
            </div>
          </div>
        </section>

        <section id="capabilities" className="marketing-section">
          <div className="section-heading">
            <div className="eyebrow">CORE CAPABILITIES</div>
            <h2>One system. Multiple engines.</h2>
            <p>
              Built to help you learn deeply, think clearly, execute reliably,
              and create without friction.
            </p>
          </div>

          <div className="pillar-grid">
            {pillars.map((pillar) => (
              <article key={pillar.title} className="card feature-card">
                <h3>{pillar.title}</h3>
                <p>{pillar.text}</p>
                <Link to={pillar.href} className="text-link">
                  Explore →
                </Link>
              </article>
            ))}
          </div>
        </section>

        <section className="marketing-section">
          <div className="section-heading">
            <div className="eyebrow">WHY IT FEELS DIFFERENT</div>
            <h2>Productivity is too small a word.</h2>
            <p>
              This is not just a chatbot with a dark coat of paint. It is an
              operating layer for learning, planning, and output.
            </p>
          </div>

          <div className="highlight-grid">
            {highlights.map((item) => (
              <div key={item} className="highlight-item">
                <span className="highlight-icon">✦</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="marketing-section founder-strip">
          <div>
            <div className="eyebrow">FOUNDER SYSTEM</div>
            <h2>Built for people who want leverage, not clutter.</h2>
            <p>
              Public users get a polished intelligence workspace. Founder mode
              unlocks private control, system oversight, and deeper operating
              power.
            </p>
          </div>

          <div className="founder-actions">
            <Link to="/pricing" className="ghost-btn link-btn">
              View Pricing
            </Link>
            <Link to="/dashboard" className="primary-btn link-btn">
              Enter SemantiqAI
            </Link>
          </div>
        </section>
      </main>
    </div>
  )
}
