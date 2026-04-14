import React, { useState } from 'react'
import { founderPost } from '../config/api'

export default function FounderControlWidget() {
  const [founderKey, setFounderKey] = useState('')
  const [objective, setObjective] = useState('Prepare SemantiqAI for elite launch')
  const [result, setResult] = useState('')

  async function generatePack() {
    const response = await founderPost('/founder/panel/command-pack', { objective }, founderKey)
    setResult(JSON.stringify(response, null, 2))
  }

  return (
    <div className="card">
      <h3>Founder Command Pack</h3>
      <p className="muted">Private strategy generation surface for internal use.</p>

      <label className="stacked-label">
        Founder Key
        <input value={founderKey} onChange={(e) => setFounderKey(e.target.value)} placeholder="Enter founder key" />
      </label>

      <label className="stacked-label">
        Objective
        <textarea rows="4" value={objective} onChange={(e) => setObjective(e.target.value)} />
      </label>

      <button className="primary-btn" onClick={generatePack}>Generate Command Pack</button>

      {result ? <pre className="result-box">{result}</pre> : null}
    </div>
  )
}
