import React, { useState, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CompliancePage from './pages/CompliancePage'
import RegulationsPage from './pages/RegulationsPage'
import AlertsPage from './pages/AlertsPage'
import PoliciesPage from './pages/PoliciesPage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

function App() {
    const [user, setUser] = useState(() => {
        const t = localStorage.getItem('token')
        if (t) return { token: t, name: localStorage.getItem('userName') || 'HR Admin', role: localStorage.getItem('userRole') || 'hr_admin', email: localStorage.getItem('userEmail') || 'hr@demo.com' }
        return null
    })

    const login = (userData) => {
        localStorage.setItem('token', userData.access_token || 'demo-token')
        localStorage.setItem('userName', userData.name || 'HR Admin')
        localStorage.setItem('userRole', userData.role || 'hr_admin')
        localStorage.setItem('userEmail', userData.email || 'hr@demo.com')
        setUser({ token: userData.access_token || 'demo-token', name: userData.name || 'HR Admin', role: userData.role || 'hr_admin', email: userData.email || 'hr@demo.com' })
    }

    const logout = () => {
        localStorage.clear()
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
                    <Route path="/" element={user ? <Layout /> : <Navigate to="/login" />}>
                        <Route index element={<DashboardPage />} />
                        <Route path="compliance" element={<CompliancePage />}/>
                        <Route path="regulations" element={<RegulationsPage />} />
                        <Route path="alerts" element={<AlertsPage />}/>
                        <Route path="policies" element={<PoliciesPage />} />
                        <Route path="reports" element={<ReportsPage />}/>
                        <Route path="settings" element={<SettingsPage />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthContext.Provider>
    )
}

export default App
