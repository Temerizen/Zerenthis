import React from 'react'
import Card from '../components/Card'

export default function LearningPage() {
  return (
    <div className="page">
      <div className="section-title">
        <h2>AI School</h2>
        <p className="muted">Curriculum, lessons, quizzes, mastery paths, and tutoring modes.</p>
      </div>

      <div className="grid three-col">
        <Card title="Subject Explorer" desc="Mathematics, science, business, programming, medicine, law, creator, and more." />
        <Card title="Lesson Builder" desc="Lesson requests, tutor mode selection, and topic depth controls." />
        <Card title="Mastery Tracking" desc="Progress cards, subject heatmaps, and long-term educational profile." />
      </div>
    </div>
  )
}
