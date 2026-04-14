import React from 'react'
import Card from '../components/Card'
import { pricingTiers } from '../config/ui'

export default function PricingPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Pricing</h2>
        <p className="muted">A launch-ready pricing surface for future Stripe integration and plan positioning.</p>
      </div>

      <div className="grid three-col">
        {pricingTiers.map((tier) => (
          <Card key={tier.name} title={tier.name} desc={tier.desc}>
            <div className="price-tag">{tier.price}</div>
            <ul className="stack-list">
              {tier.features.map((feature) => <li key={feature}>{feature}</li>)}
            </ul>
            <button className="primary-btn wide-btn">Choose {tier.name}</button>
          </Card>
        ))}
      </div>
    </div>
  )
}
