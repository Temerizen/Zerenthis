const pillars = [
  {
    title: "Premium Document Forge",
    text: "Create polished digital products, reports, guides, and sellable knowledge assets with a refinement-first workflow.",
  },
  {
    title: "Video Content Engine",
    text: "Turn one strong idea into YouTube scripts, Shorts, TikTok-ready angles, hooks, and content packs built for momentum.",
  },
  {
    title: "Director Control Layer",
    text: "Talk to the AI like a creative director. Revise, expand, sharpen, simplify, and approve outputs before publishing.",
  },
  {
    title: "Single-Flow Quality System",
    text: "No sloppy batch spam. Zerenthis focuses on one item at a time so every product has room to become premium.",
  },
];

const workflow = [
  "Choose one high-value idea",
  "Generate a master asset",
  "Refine with AI supervision",
  "Split into product + content",
  "Approve, export, and post",
];

const cards = [
  {
    eyebrow: "Documents",
    title: "Sell premium digital products",
    body: "Guides, frameworks, research-style PDFs, and authority assets built to look worth paying for.",
  },
  {
    eyebrow: "Shorts",
    title: "Turn ideas into attention",
    body: "Create punchy short-form scripts for TikTok and YouTube Shorts from the same core intelligence.",
  },
  {
    eyebrow: "YouTube",
    title: "Build trust at scale",
    body: "Expand winning concepts into longer scripts that deepen authority and feed traffic back into your products.",
  },
];

export default function HomePage() {
  return (
    <main className="site-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">Z</div>
          <div>
            <div className="brand-title">Zerenthis</div>
            <div className="brand-subtitle">Intelligent Creation Engine</div>
          </div>
        </div>

        <nav className="topnav">
          <a href="#vision">Vision</a>
          <a href="#pillars">Capabilities</a>
          <a href="#workflow">Flow</a>
          <a href="#launch">Launch</a>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">AI-powered creation, refined for real output</div>
          <h1>
            Build premium products and content from one idea
            <span className="gradient-text"> without drowning in chaos.</span>
          </h1>
          <p className="hero-text">
            Zerenthis is designed to turn a single high-value concept into
            premium documents, YouTube scripts, and short-form content with a
            quality-first workflow you can actually supervise.
          </p>

          <div className="hero-actions">
            <a className="btn btn-primary" href="#launch">
              Start building
            </a>
            <a className="btn btn-secondary" href="#pillars">
              See capabilities
            </a>
          </div>

          <div className="hero-stats">
            <div className="stat">
              <span className="stat-value">1 Idea</span>
              <span className="stat-label">becomes a full asset chain</span>
            </div>
            <div className="stat">
              <span className="stat-value">Single Flow</span>
              <span className="stat-label">designed for quality over clutter</span>
            </div>
            <div className="stat">
              <span className="stat-value">Director Mode</span>
              <span className="stat-label">chat-based supervision and edits</span>
            </div>
          </div>
        </div>

        <div className="hero-panel">
          <div className="panel-glow" />
          <div className="panel-card">
            <div className="panel-label">Core Loop</div>
            <div className="panel-flow">
              <span>Idea</span>
              <span>→</span>
              <span>Master Asset</span>
              <span>→</span>
              <span>Document</span>
              <span>+</span>
              <span>Video Scripts</span>
            </div>

            <div className="panel-block">
              <h3>What it should feel like</h3>
              <p>
                Less like a text vending machine. More like an AI studio with
                taste, control, and momentum.
              </p>
            </div>

            <div className="panel-block">
              <h3>Primary mission</h3>
              <p>
                Create outputs that are worth posting, worth packaging, and
                eventually worth paying for.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section id="vision" className="section">
        <div className="section-heading">
          <div className="eyebrow">Vision</div>
          <h2>A focused creation system with polish, leverage, and direction</h2>
          <p>
            Zerenthis is moving away from batch clutter and toward a premium
            single-product pipeline that transforms one sharp concept into a
            whole content ecosystem.
          </p>
        </div>

        <div className="card-grid three">
          {cards.map((card) => (
            <article key={card.title} className="info-card">
              <div className="card-eyebrow">{card.eyebrow}</div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="pillars" className="section">
        <div className="section-heading">
          <div className="eyebrow">Capabilities</div>
          <h2>The four pillars of the system</h2>
        </div>

        <div className="pillars-grid">
          {pillars.map((pillar) => (
            <article key={pillar.title} className="pillar-card">
              <div className="pillar-icon">◆</div>
              <h3>{pillar.title}</h3>
              <p>{pillar.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="workflow" className="section workflow-section">
        <div className="section-heading">
          <div className="eyebrow">Flow</div>
          <h2>Simple enough to move fast, structured enough to stay premium</h2>
        </div>

        <div className="workflow-list">
          {workflow.map((step, index) => (
            <div key={step} className="workflow-item">
              <div className="workflow-number">{index + 1}</div>
              <div className="workflow-text">{step}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="launch" className="section cta-section">
        <div className="cta-card">
          <div className="eyebrow">Launch direction</div>
          <h2>Ship a site that feels like a mission control room for creation</h2>
          <p>
            Start with the premium document pipeline, short-form content output,
            and AI director chat. Nail those three, and the rest becomes an
            expansion instead of a rescue mission.
          </p>

          <div className="hero-actions">
            <a className="btn btn-primary" href="https://github.com/Temerizen">
              View GitHub
            </a>
            <a className="btn btn-secondary" href="#vision">
              Back to top
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}