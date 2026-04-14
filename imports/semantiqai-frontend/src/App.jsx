import React from "react"
import { Routes, Route } from "react-router-dom"
import HomePage from "./pages/HomePage"
import DashboardPage from "./pages/DashboardPage"
import PricingPage from "./pages/PricingPage"
import LoginPage from "./pages/LoginPage"
import FounderPage from "./pages/FounderPage"
import LearningPage from "./pages/LearningPage"
import CognitivePage from "./pages/CognitivePage"
import ExecutionPage from "./pages/ExecutionPage"
import SimulationPage from "./pages/SimulationPage"
import CreationPage from "./pages/CreationPage"

function PlaceholderPage({ title, text }) {
  return (
    <div className="page">
      <div className="section-title">
        <h2>{title}</h2>
        <p className="muted">{text}</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/founder" element={<FounderPage />} />

      <Route path="/school" element={<LearningPage />} />
      <Route path="/cognitive-lab" element={<CognitivePage />} />
      <Route path="/execution" element={<ExecutionPage />} />
      <Route path="/simulation" element={<SimulationPage />} />
      <Route path="/creation" element={<CreationPage />} />

      <Route
        path="*"
        element={
          <PlaceholderPage
            title="Page not found"
            text="This route is not wired yet."
          />
        }
      />
    </Routes>
  )
}
