import React from 'react'

export default function StatGrid() {
  const stats = [
    { label: 'Core Systems', value: '10+' },
    { label: 'Founder Layers', value: 'Private' },
    { label: 'Modes', value: 'Multi-Agent' },
    { label: 'Launch Shape', value: 'Near Final' }
  ]

  return (
    <div className="stats">
      {stats.map((item) => (
        <div key={item.label} className="stat">
          <div className="stat-value">{item.value}</div>
          <div className="stat-label">{item.label}</div>
        </div>
      ))}
    </div>
  )
}
