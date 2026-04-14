import React from 'react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/school', label: 'AI School' },
  { path: '/cognitive-lab', label: 'Cognitive Lab' },
  { path: '/execution', label: 'Execution Engine' },
  { path: '/simulation', label: 'Reality Simulation' },
  { path: '/creation', label: 'Infinite Creation' },
  { path: '/pricing', label: 'Pricing' },
  { path: '/founder', label: 'Founder Control' }
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">SA</div>
        <div>
          <div className="brand-title">SemantiqAI</div>
          <div className="brand-sub">Ascension</div>
        </div>
      </div>

      <nav className="nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            end={item.path === '/'}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
