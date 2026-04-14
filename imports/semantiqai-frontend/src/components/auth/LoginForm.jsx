import React, { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'

export default function LoginForm() {
  const { login, isAuthenticated, role, logout } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await login(username, password)

    if (result?.ok && result?.data?.token) {
      setMessage('Login successful.')
    } else {
      setMessage(
        result?.error?.message ||
        result?.error ||
        'Login failed.'
      )
    }
  }

  return (
    <div className="auth-box">
      {isAuthenticated ? (
        <div className="auth-state">
          <p className="muted">Signed in as <strong>{role}</strong>.</p>
          <button className="ghost-btn" onClick={logout}>Sign Out</button>
        </div>
      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" />
          </label>

          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" />
          </label>

          <button type="submit" className="primary-btn">Sign In</button>
          {message ? <p className="muted">{message}</p> : null}
        </form>
      )}
    </div>
  )
}
