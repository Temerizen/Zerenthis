import { useState } from 'react'
import { apiPost } from '../config/api'
import { setAuth, clearAuth, getRole, getToken } from '../state/auth'

export function useAuth() {
  const [token, setToken] = useState(getToken())
  const [role, setRole] = useState(getRole())

  async function login(username, password) {
    const result = await apiPost('/auth/login', { username, password })
    const payload = result?.data || result

    if (result?.ok && payload?.token) {
      setAuth(payload.token, payload.role || 'user')
      setToken(payload.token)
      setRole(payload.role || 'user')
    }

    return result
  }

  function logout() {
    clearAuth()
    setToken('')
    setRole('guest')
  }

  return {
    token,
    role,
    isFounder: role === 'founder',
    isAdmin: role === 'admin' || role === 'founder',
    isAuthenticated: !!token,
    login,
    logout
  }
}
