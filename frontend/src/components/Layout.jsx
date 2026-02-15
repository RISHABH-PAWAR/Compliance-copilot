import React from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../App'
import { LayoutDashboard, Shield, ScrollText, Bell, FileText, BarChart3, Settings, LogOut, Search } from 'lucide-react'

const navItems = [
    {
        section: 'Overview', items: [
            { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
            { to: '/compliance', icon: Shield, label: 'Compliance Engine' },
        ]
    },
    {
        section: 'Intelligence', items: [
            { to: '/regulations', icon: ScrollText, label: 'Regulations', badge: '7' },
            { to: '/alerts', icon: Bell, label: 'Alerts', badge: '3' },
        ]
    },
    {
        section: 'Documents', items: [
            { to: '/policies', icon: FileText, label: 'Policies' },
            { to: '/reports', icon: BarChart3, label: 'Reports' },
        ]
    },
    {
        section: 'System', items: [
            { to: '/settings', icon: Settings, label: 'Settings' },
        ]
    },
]

const pageTitles = {
    '/': { title: 'Command Center', subtitle: 'Real-time compliance intelligence dashboard' },
    '/compliance': { title: 'Compliance Engine', subtitle: 'AI-powered gap analysis & risk scoring' },
    '/regulations': { title: 'Regulatory Intelligence', subtitle: 'Indian labor law monitoring & diff engine' },
    '/alerts': { title: 'Alert Center', subtitle: 'Critical compliance notifications' },
    '/policies': { title: 'Policy Vault', subtitle: 'Company HR document management' },
    '/reports': { title: 'Report Generator', subtitle: 'Compliance reports & audit packs' },
    '/settings': { title: 'Settings', subtitle: 'System configuration' },
}

export default function Layout() {
    const { user, logout } = useAuth()
    const location = useLocation()
    const pageInfo = pageTitles[location.pathname] || pageTitles['/']

    return (
        <div className="app-layout">
            <aside className="sidebar">
                <div className="sidebar-logo">
                    <div className="logo-icon">⚖️</div>
                    <div className="logo-text">
                        <span>Compliance Copilot</span>
                        <span>Labor Law AI</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map((section) => (
                        <div key={section.section}>
                            <div className="nav-section-title">{section.section}</div>
                            {section.items.map((item) => (
                                <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                                    <item.icon className="nav-icon" size={18} />
                                    <span>{item.label}</span>
                                    {item.badge && <span className="nav-badge">{item.badge}</span>}
                                </NavLink>
                            ))}
                        </div>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="sidebar-user">
                        <div className="user-avatar">{(user?.name || 'U')[0]}</div>
                        <div className="user-info">
                            <div className="user-name">{user?.name || 'User'}</div>
                            <div className="user-role">{user?.role?.replace('_', ' ')}</div>
                        </div>
                    </div>
                    <button className="btn btn-ghost" style={{ width: '100%', marginTop: 8, justifyContent: 'center' }} onClick={logout}>
                        <LogOut size={14} /> Sign Out
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <header className="header">
                    <div className="header-left">
                        <h1>{pageInfo.title}</h1>
                        <p>{pageInfo.subtitle}</p>
                    </div>
                    <div className="header-right">
                        <button className="header-btn" title="Search"><Search size={16} /></button>
                        <button className="header-btn" title="Notifications">
                            <Bell size={16} />
                            <span className="notification-dot" />
                        </button>
                    </div>
                </header>
                <div className="page-content animate-in">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}
