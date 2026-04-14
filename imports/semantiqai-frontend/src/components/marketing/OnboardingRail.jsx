import React from 'react'
import Card from '../Card'

export default function OnboardingRail() {
  const items = [
    {
      title: '1. Choose Your Path',
      desc: 'Start in learning, cognition, execution, simulation, or creation.'
    },
    {
      title: '2. Build Your Profile',
      desc: 'Track mastery, momentum, and system usage over time.'
    },
    {
      title: '3. Upgrade Intelligently',
      desc: 'Move from exploration into serious usage with premium layers.'
    }
  ]

  return (
    <div className="grid three-col">
      {items.map((item) => (
        <Card key={item.title} title={item.title} desc={item.desc} />
      ))}
    </div>
  )
}
