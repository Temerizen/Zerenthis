import React from 'react'
import LoginForm from '../components/auth/LoginForm'
import Card from '../components/Card'

export default function LoginPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>Sign In</h2>
        <p className="muted">Access your SemantiqAI workspace and role-specific surfaces.</p>
      </div>

      <div className="grid two-col">
        <Card title="Access Platform" desc="Use your account to enter the system and unlock your layer.">
          <LoginForm />
        </Card>

        <Card title="Why Sign In?" desc="Authentication enables protected tools, founder isolation, and personalized progress.">
          <ul className="stack-list">
            <li>Protected routes and role separation</li>
            <li>Learning and cognitive progression</li>
            <li>Execution and creation continuity</li>
            <li>Founder-only internal command surfaces</li>
          </ul>
        </Card>
      </div>
    </div>
  )
}
