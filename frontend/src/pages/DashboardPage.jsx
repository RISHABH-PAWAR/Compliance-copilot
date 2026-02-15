import React, { useState, useEffect } from 'react'
import { Shield, AlertTriangle, TrendingUp, TrendingDown, FileCheck, DollarSign, Bell, Clock, ChevronRight, Activity, Zap, Info } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { dashboardApi } from '../api'

const EMPTY_DATA = {
    compliance_score: 0, total_gaps: 0, critical_gaps: 0, high_gaps: 0, medium_gaps: 0, low_gaps: 0,
    total_financial_exposure: 0, active_alerts: 0, pending_actions: 0, regulations_tracked: 0, recent_changes: 0,
    top_violations: [],
    recent_alerts: [],
    trend_data: [],
    checklist: [],
}

const PIE_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e']

const formatINR = (n) => {
    if (!n) return '₹0'
    if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)} Cr`
    if (n >= 100000) return `₹${(n / 100000).toFixed(1)} L`
    return `₹${n.toLocaleString('en-IN')}`
}

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
        <div style={{ background: '#1a1f2e', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
            <div style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</div>
            {payload.map((p, i) => <div key={i} style={{ color: p.color }}>{p.name}: {p.value}</div>)}
        </div>
    )
}

export default function DashboardPage() {
    const [data, setData] = useState(EMPTY_DATA)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchDashboardData = async () => {
        try {
            setLoading(true)
            const response = await dashboardApi.hr()
            setData(response.data)
            setError(null)
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err)
            setError('Unable to load dashboard data. Please ensure you are logged in and the backend is running.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchDashboardData()
    }, [])

    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading your compliance dashboard...</div>

    if (error) return (
        <div style={{ padding: 40, textAlign: 'center' }}>
            <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: 16 }} />
            <div style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 8 }}>Connectivity Issue</div>
            <div style={{ color: '#94a3b8', fontSize: 14, maxWidth: 400, margin: '0 auto', marginBottom: 24 }}>{error}</div>
            <button className="btn btn-primary" onClick={fetchDashboardData}>Try Again</button>
        </div>
    )

    const scoreColor = data.compliance_score >= 70 ? '#22c55e' : data.compliance_score >= 50 ? '#eab308' : '#ef4444'
    const gapPie = [
        { name: 'Critical', value: data.critical_gaps || 0 },
        { name: 'High', value: data.high_gaps || 0 },
        { name: 'Medium', value: data.medium_gaps || 0 },
        { name: 'Low', value: data.low_gaps || 0 },
    ]

    const hasData = data.total_gaps > 0 || data.recent_alerts?.length > 0 || data.top_violations?.length > 0

    return (
        <div>
            {/* Stats Row */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-header">
                        <div className="stat-icon accent"><Shield size={18} /></div>
                    </div>
                    <div className="stat-value" style={{ color: scoreColor }}>{data.compliance_score || 0}%</div>
                    <div className="stat-label">Overall Compliance Score</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header">
                        <div className="stat-icon critical"><AlertTriangle size={18} /></div>
                    </div>
                    <div className="stat-value">{data.total_gaps || 0}</div>
                    <div className="stat-label">Compliance Gaps Found</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header">
                        <div className="stat-icon high"><DollarSign size={18} /></div>
                    </div>
                    <div className="stat-value">{formatINR(data.total_financial_exposure)}</div>
                    <div className="stat-label">Financial Exposure</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header">
                        <div className="stat-icon info"><Bell size={18} /></div>
                    </div>
                    <div className="stat-value">{data.active_alerts || 0}</div>
                    <div className="stat-label">Active Alerts</div>
                </div>
            </div>

            {!hasData ? (
                <div className="card" style={{ marginTop: 24, textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ width: 64, height: 64, background: 'rgba(99,102,241,0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8', margin: '0 auto 20px' }}>
                        <Info size={32} />
                    </div>
                    <h2 style={{ fontSize: 20, color: '#f1f5f9', marginBottom: 12 }}>Welcome to your Zero-Gap Dashboard</h2>
                    <p style={{ color: '#94a3b8', maxWidth: 500, margin: '0 auto 24px', lineHeight: 1.6 }}>
                        No compliance data found. Start by uploading your company policies or employee handbook in the
                        <strong> Documents</strong> section. Our AI will analyze them and populate this dashboard automatically.
                    </p>
                    <a href="/policies" className="btn btn-primary">Go to Policies Section</a>
                </div>
            ) : (
                <>
                    {/* Trend + Gap Breakdown */}
                    <div className="content-grid" style={{ marginBottom: 20 }}>
                        <div className="card">
                            <div className="card-title"><Activity size={14} className="icon" /> Compliance Trend</div>
                            {data.trend_data?.length > 0 ? (
                                <ResponsiveContainer width="100%" height={220}>
                                    <AreaChart data={data.trend_data}>
                                        <defs>
                                            <linearGradient id="gScore" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                                                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
                                        <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                        <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Area type="monotone" dataKey="compliance_score" name="Score" stroke="#6366f1" fill="url(#gScore)" strokeWidth={2.5} dot={{ fill: '#6366f1', r: 3 }} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: 13 }}>No trend data yet.</div>
                            )}
                        </div>

                        <div className="card">
                            <div className="card-title"><Zap size={14} className="icon" /> Gap Severity Breakdown</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
                                <ResponsiveContainer width={160} height={160}>
                                    <PieChart>
                                        <Pie data={gapPie} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value" stroke="none">
                                            {gapPie.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                                        </Pie>
                                    </PieChart>
                                </ResponsiveContainer>
                                <div style={{ flex: 1 }}>
                                    {gapPie.map((item, i) => (
                                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0' }}>
                                            <div style={{ width: 10, height: 10, borderRadius: 3, background: PIE_COLORS[i], flexShrink: 0 }} />
                                            <span style={{ flex: 1, fontSize: 13, color: '#94a3b8' }}>{item.name}</span>
                                            <span style={{ fontSize: 16, fontWeight: 700, color: '#f1f5f9' }}>{item.value}</span>
                                        </div>
                                    ))}
                                    <div style={{ marginTop: 8, padding: '8px 12px', background: 'rgba(239,68,68,0.08)', borderRadius: 8, fontSize: 12, color: '#ef4444' }}>
                                        <strong>{(data.critical_gaps || 0) + (data.high_gaps || 0)}</strong> items need immediate action
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Violations + Alerts */}
                    <div className="content-grid">
                        <div className="card">
                            <div className="card-title"><AlertTriangle size={14} className="icon" /> Top Compliance Violations</div>
                            <div className="item-list">
                                {data.top_violations?.length > 0 ? data.top_violations.map((v, i) => (
                                    <div className="list-item" key={i}>
                                        <div className="item-icon" style={{ background: v.risk_level === 'critical' ? 'rgba(239,68,68,0.12)' : v.risk_level === 'high' ? 'rgba(249,115,22,0.12)' : 'rgba(234,179,8,0.12)', color: v.risk_level === 'critical' ? '#ef4444' : v.risk_level === 'high' ? '#f97316' : '#eab308' }}>
                                            <AlertTriangle size={14} />
                                        </div>
                                        <div className="item-content">
                                            <div className="item-title">{v.gap || v.gap_description}</div>
                                            <div className="item-desc">{v.act_name} • {v.section || v.section_number}</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <span className={`badge ${v.risk_level}`}>{v.risk_level}</span>
                                            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{formatINR(v.estimated_penalty)}</div>
                                        </div>
                                    </div>
                                )) : <div style={{ padding: 20, color: '#64748b', textAlign: 'center' }}>No violations detected. Good work!</div>}
                            </div>
                        </div>

                        <div className="card">
                            <div className="card-title"><Bell size={14} className="icon" /> Recent Alerts</div>
                            <div className="item-list">
                                {data.recent_alerts?.length > 0 ? data.recent_alerts.map((a, i) => (
                                    <div className="list-item" key={i} style={{ opacity: a.is_read ? 0.6 : 1 }}>
                                        <div className="item-icon" style={{ background: a.priority === 'critical' ? 'rgba(239,68,68,0.12)' : a.priority === 'high' ? 'rgba(249,115,22,0.12)' : 'rgba(234,179,8,0.12)', color: a.priority === 'critical' ? '#ef4444' : a.priority === 'high' ? '#f97316' : '#eab308' }}>
                                            <Bell size={14} />
                                        </div>
                                        <div className="item-content">
                                            <div className="item-title">{a.title}</div>
                                            <div className="item-desc">{a.created_at}</div>
                                        </div>
                                        <span className={`badge ${a.priority}`}>{a.priority}</span>
                                    </div>
                                )) : <div style={{ padding: 20, color: '#64748b', textAlign: 'center' }}>No recent alerts.</div>}
                            </div>
                        </div>
                    </div>

                    {/* Checklist */}
                    {data.checklist?.length > 0 && (
                        <div className="card" style={{ marginTop: 20 }}>
                            <div className="card-title"><FileCheck size={14} className="icon" /> Priority Compliance Checklist</div>
                            {data.checklist.map((item, i) => (
                                <div className="checklist-item" key={i}>
                                    <div className="checklist-checkbox" style={item.status === 'completed' ? { background: '#6366f1', borderColor: '#6366f1' } : {}}>
                                        {item.status === 'completed' && '✓'}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div className={`checklist-text ${item.status === 'completed' ? 'completed' : ''}`}>{item.title}</div>
                                        <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                                            <span className={`badge ${item.priority}`}>{item.priority}</span>
                                            <span style={{ fontSize: 11, color: '#64748b' }}><Clock size={10} style={{ verticalAlign: '-1px' }} /> Due: {item.deadline}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
