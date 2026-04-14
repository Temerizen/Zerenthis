import React from 'react'
import Card from '../components/Card'

export default function CreationPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Infinite Creation Engine</h2>
        <p className="muted">Books, podcasts, movies, games, universes, lore, and monetizable IP systems.</p>
      </div>

      <div className="grid three-col">
        <Card title="Creative Bundle Builder" desc="Generate multi-format concept packs from a single core idea." />
        <Card title="Universe Forge" desc="Build worlds, factions, histories, conflicts, and lore systems." />
        <Card title="IP Foundry" desc="Founder monetization and expansion logic for scalable creative properties." />
      </div>
    </div>
  )
}
