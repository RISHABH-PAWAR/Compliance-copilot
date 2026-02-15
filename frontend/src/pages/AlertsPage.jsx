import React, { useState, useEffect } from 'react'
import { Bell, Check, X, Filter, AlertTriangle, Info } from 'lucide-react'
import { alertApi } from '../api'

const typeLabels = {
    regulation_update: 'Regulation Update',
    compliance_gap: 'Compliance Gap',
    deadline: 'Deadline',
    verification: 'Verification'
}

export default function AlertsPage() {
    const [alerts, setAlerts] = useState([])
    const [filter, setFilter] = useState('all')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchAlerts = async () => {
        try {
            setLoading(true)
            const response = await alertApi.list()
            setAlerts(response.data.alerts || response.data || [])
            setError(null)
        } catch (err) {
            console.error('Failed to fetch alerts:', err)
            setError('Unable to load alerts. Please check your connection.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchAlerts()
    }, [])

    const filtered = (Array.isArray(alerts) ? alerts : []).filter(a => {
        if (filter === 'all') return true
        if (filter === 'unread') return !a.is_read
        return a.priority === filter
    })

    const markRead = async (id) => {
        try {
            await alertApi.markRead(id)
            setAlerts(prev => prev.map(a => a.id === id ? { ...a, is_read: true } : a))
        } catch (err) {
            console.error('Failed to mark alert as read:', err)
        }
    }

    const dismiss = async (id) => {
        try {
            await alertApi.dismiss(id)
            setAlerts(prev => prev.filter(a => a.id !== id))
        } catch (err) {
            setAlerts(prev => prev.filter(a => a.id !== id)) // Optimistic dismiss
        }
    }

    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Checking for compliance alerts...</div>

    if (error) return (
        <div style={{ padding: 40, textAlign: 'center' }}>
            <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: 16 }} />
            <div style={{ color: '#f1f5f9', fontWeight: 600 }}>Alerts Unavailable</div>
            <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 4 }}>{error}</div>
        </div>
    )

    return (
        <div>
            <div style={{ display: 'flex', gap: 6, marginBottom: 20, flexWrap: 'wrap' }}>
                {[['all', 'All'], ['unread', `Unread (${alerts.filter(a => !a.is_read).length})`], ['critical', 'Critical'], ['high', 'High'], ['medium', 'Medium']].map(([key, label]) => (
                    <button key={key} className={`btn ${filter === key ? 'btn-primary' : 'btn-ghost'}`} style={{ fontSize: 12 }} onClick={() => setFilter(key)}>{label}</button>
                ))}
            </div>

            <div className="item-list" style={{ gap: 12 }}>
                {filtered.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                        <Info size={32} style={{ color: '#64748b', margin: '0 auto 12px' }} theme="outline" />
                        <div style={{ color: '#f1f5f9', fontWeight: 600 }}>No Alerts Found</div>
                        <div style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Your workspace is currently compliant.</div>
                    </div>
                ) : filtered.map((alert) => (
                    <div key={alert.id} className="card" style={{ padding: '16px 20px', opacity: alert.is_read ? 0.7 : 1, borderLeft: `3px solid ${alert.priority === 'critical' ? '#ef4444' : alert.priority === 'high' ? '#f97316' : alert.priority === 'medium' ? '#eab308' : '#22c55e'}` }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                    <span className={`badge ${alert.priority}`}>{alert.priority}</span>
                                    <span className="badge info">{typeLabels[alert.type] || alert.type}</span>
                                    {!alert.is_read && <span style={{ width: 8, height: 8, background: '#6366f1', borderRadius: '50%' }} />}
                                </div>
                                <div style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9', marginBottom: 6 }}>{alert.title}</div>
                                <div style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.5 }}>{alert.description}</div>
                                <div style={{ fontSize: 11, color: '#64748b', marginTop: 8 }}>{alert.created_at || 'Just now'}</div>
                            </div>
                            <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                                {!alert.is_read && <button className="btn btn-ghost" style={{ padding: 6 }} onClick={() => markRead(alert.id)} title="Mark as read"><Check size={14} /></button>}
                                <button className="btn btn-ghost" style={{ padding: 6 }} onClick={() => dismiss(alert.id)} title="Dismiss"><X size={14} /></button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
