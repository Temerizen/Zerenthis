import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

export default function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-shell">
        <Header />
        <div className="page-shell">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
