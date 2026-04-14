import React from "react"
import { Link, useLocation } from "react-router-dom"

export default function Header({ isAuthenticated = false, role = "Guest" }) {
  const location = useLocation()
  const isHome = location.pathname === "/"

  return (
    <header className={`topbar ${isHome ? "topbar-home" : ""}`}>
      <div className="topbar-brand">
        <Link to="/" className="brand-link">
          <span className="brand-mark">SA</span>
          <span>SemantiqAI</span>
        </Link>
      </div>

      <nav className="topbar-nav">
        <Link className="ghost-btn link-btn" to="/pricing">
          Pricing
        </Link>
        <Link className="ghost-btn link-btn" to="/school">
          AI School
        </Link>
        <Link className="ghost-btn link-btn" to="/creation">
          Creation
        </Link>
      </nav>

      <div className="topbar-actions">
        <Link className="ghost-btn link-btn" to="/login">
          {isAuthenticated ? `Role: ${role}` : "Sign In"}
        </Link>
        <Link className="primary-btn link-btn" to="/dashboard">
          {isHome ? "Open App" : "Dashboard"}
        </Link>
      </div>
    </header>
  )
}
