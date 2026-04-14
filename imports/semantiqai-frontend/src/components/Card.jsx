import React from "react"
import { Link } from "react-router-dom"

export default function Card({ title, desc, to }) {
  const content = (
    <>
      <h3>{title}</h3>
      <p>{desc}</p>
    </>
  )

  if (to) {
    return (
      <Link to={to} className="card" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
        {content}
      </Link>
    )
  }

  return <div className="card">{content}</div>
}
