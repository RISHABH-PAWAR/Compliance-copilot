import React, { useState, useEffect } from 'react'
import { Shield, AlertTriangle, Map, FileCheck, ChevronRight, TrendingUp, Activity, Target, Info } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import { complianceApi } from '../api'

const formatINR = (n) => {
    if (!n) return '₹0'
    return n >= 100000 ? `₹${(n / 100000).toFixed(1)}L` : `₹${n.toLocaleString('en-IN')}`
}

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (<div style={{ background: '#1a1f2e', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
        <div style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</div>
        {payload.map((p, i) => <div key={i} style={{ color: p.color }}>{p.name}: {p.value}</div>)}
    </div>)
}

export default function CompliancePage() {
    const [tab, setTab] = useState('gaps')
    const [expanded, setExpanded] = useState(null)
    const [gaps, setGaps] = useState([])
    const [overview, setOverview] = useState({ score: 0, total_gaps: 0, critical_gaps: 0, rules_checked: 0, states: 0 })
    const [stateMap, setStateMap] = useState([])
    const [radarData, setRadarData] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchData = async () => {
        try {
            setLoading(true)
            const [gRes, oRes, smRes] = await Promise.all([
                complianceApi.gaps(),
                complianceApi.overview(),
                complianceApi.stateMap()
            ])
            setGaps(gRes.data.gaps || [])
            setOverview(oRes.data || { score: 0, total_gaps: 0, critical_gaps: 0, rules_checked: 0, states: 0 })
            setStateMap(smRes.data || [])

            // Generate mock-free radar data structure if empty
            if (smRes.data?.radar) {
                setRadarData(smRes.data.radar)
            } else {
                setRadarData([])
            }

            setError(null)
        } catch (err) {
            console.error('Failed to fetch compliance data:', err)
            setError('Unable to load compliance analysis. Please ensure you have uploaded documents and have an active session.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Calculating compliance metrics...</div>

    if (error) return (
        <div style={{ padding: 40, textAlign: 'center' }}>
            <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: 16 }} />
            <div style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 8 }}>Analysis Error</div>
            <div style={{ color: '#94a3b8', fontSize: 14, maxWidth: 400, margin: '0 auto', marginBottom: 24 }}>{error}</div>
            <button className="btn btn-primary" onClick={fetchData}>Retry Analysis</button>
        </div>
    )

    const hasData = gaps.length > 0 || stateMap.length > 0

    return (
        <div>
            {/* Summary Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-header"><div className="stat-icon accent"><Shield size={18} /></div></div>
                    <div className="stat-value" style={{ color: overview.score >= 70 ? '#22c55e' : '#eab308' }}>{overview.score || 0}%</div>
                    <div className="stat-label">Compliance Score</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header"><div className="stat-icon critical"><AlertTriangle size={18} /></div></div>
                    <div className="stat-value">{overview.total_gaps || 0}</div>
                    <div className="stat-label">Total Gaps • {overview.critical_gaps || 0} Critical</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header"><div className="stat-icon high"><Target size={18} /></div></div>
                    <div className="stat-value">{overview.rules_checked || 0}</div>
                    <div className="stat-label">Rules Checked</div>
                </div>
                <div className="stat-card">
                    <div className="stat-header"><div className="stat-icon info"><Map size={18} /></div></div>
                    <div className="stat-value">{overview.states || 0}</div>
                    <div className="stat-label">States Monitored</div>
                </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 20, background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', padding: 4, width: 'fit-content' }}>
                {[['gaps', 'Gap Analysis'], ['states', 'State Map'], ['radar', 'Risk Radar']].map(([key, label]) => (
                    <button key={key} className={`btn ${tab === key ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab(key)}>{label}</button>
                ))}
            </div>

            {!hasData ? (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ width: 64, height: 64, background: 'rgba(99,102,241,0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8', margin: '0 auto 20px' }}>
                        <Info size={32} />
                    </div>
                    <h2 style={{ fontSize: 20, color: '#f1f5f9', marginBottom: 12 }}>No Compliance Gaps Detected</h2>
                    <p style={{ color: '#94a3b8', maxWidth: 500, margin: '0 auto 24px', lineHeight: 1.6 }}>
                        To generate a gap analysis, please upload your company policy documents.
                        Our AI compares your internal rules against the latest Indian labor law regulations.
                    </p>
                    <a href="/policies" className="btn btn-primary">Upload Policies</a>
                </div>
            ) : (
                <>
                    {tab === 'gaps' && (
                        <div className="card">
                            <div className="card-title"><AlertTriangle size={14} className="icon" /> Compliance Gaps — Ordered by Risk Score</div>
                            <div className="item-list">
                                {gaps.length > 0 ? gaps.map((gap) => (
                                    <div key={gap.id}>
                                        <div className="list-item" style={{ cursor: 'pointer' }} onClick={() => setExpanded(expanded === gap.id ? null : gap.id)}>
                                            <div className="item-icon" style={{ background: gap.risk_level === 'critical' ? 'rgba(239,68,68,0.12)' : gap.risk_level === 'high' ? 'rgba(249,115,22,0.12)' : gap.risk_level === 'medium' ? 'rgba(234,179,8,0.12)' : 'rgba(34,197,94,0.12)', color: gap.risk_level === 'critical' ? '#ef4444' : gap.risk_level === 'high' ? '#f97316' : gap.risk_level === 'medium' ? '#eab308' : '#22c55e' }}>
                                                <AlertTriangle size={14} />
                                            </div>
                                            <div className="item-content">
                                                <div className="item-title">{gap.gap || gap.gap_description}</div>
                                                <div className="item-desc">{gap.act_name} • {gap.section || gap.section_number} • {gap.affected_employees || 0} employees affected</div>
                                            </div>
                                            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                                <span className={`badge ${gap.risk_level}`}>Risk: {gap.risk_score}</span>
                                                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{formatINR(gap.estimated_penalty)}</div>
                                            </div>
                                            <ChevronRight size={16} style={{ color: '#64748b', transform: expanded === gap.id ? 'rotate(90deg)' : 'none', transition: '0.2s' }} />
                                        </div>
                                        {expanded === gap.id && (
                                            <div style={{ padding: '16px 20px 16px 60px', background: 'var(--bg-elevated)', borderRadius: '0 0 10px 10px', marginTop: -4, animation: 'fadeIn 0.3s ease' }}>
                                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 13 }}>
                                                    <div><span style={{ color: '#64748b' }}>Corrective Action:</span><div style={{ color: '#f1f5f9', marginTop: 4 }}>{gap.corrective_action}</div></div>
                                                    <div><span style={{ color: '#64748b' }}>Status:</span><div style={{ marginTop: 4 }}><span className={`badge ${gap.status === 'in_progress' ? 'info' : 'medium'}`}>{gap.status}</span></div>
                                                        <div style={{ color: '#64748b', marginTop: 8 }}>Deadline: <span style={{ color: '#f1f5f9' }}>{gap.deadline}</span></div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )) : <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>No gaps detected.</div>}
                            </div>
                        </div>
                    )}

                    {tab === 'states' && (
                        <div className="content-grid">
                            <div className="card">
                                <div className="card-title"><Map size={14} className="icon" /> State-Wise Compliance</div>
                                {stateMap.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={stateMap}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
                                            <XAxis dataKey="state" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} />
                                            <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} />
                                            <Tooltip content={<CustomTooltip />} />
                                            < Bar dataKey="compliance_score" name="Compliance %" radius={[6, 6, 0, 0]}>
                                                {stateMap.map((s, i) => <Cell key={i} fill={s.color || '#6366f1'} />)}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>No state data available.</div>}
                            </div>
                            <div className="card">
                                <div className="card-title"><Activity size={14} className="icon" /> State Details</div>
                                <div className="item-list">
                                    {stateMap.length > 0 ? stateMap.map((s, i) => (
                                        <div className="list-item" key={i}>
                                            <div className="item-icon" style={{ background: `${s.color || '#6366f1'}20`, color: s.color || '#6366f1', fontSize: 12, fontWeight: 700 }}>{s.state[0]}{s.state[1]}</div>
                                            <div className="item-content">
                                                <div className="item-title">{s.state}</div>
                                                <div className="item-desc">{s.regulations_applicable || 0} acts • {s.gaps || 0} gaps • {formatINR(s.financial_exposure)} exposure</div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: 18, fontWeight: 700, color: s.color || '#6366f1' }}>{s.compliance_score}%</div>
                                                {s.critical > 0 && <span className="badge critical">{s.critical} critical</span>}
                                            </div>
                                        </div>
                                    )) : <div style={{ padding: 20, color: '#64748b', textAlign: 'center' }}>N/A</div>}
                                </div>
                            </div>
                        </div>
                    )}

                    {tab === 'radar' && (
                        <div className="card" style={{ maxWidth: 600 }}>
                            <div className="card-title"><Target size={14} className="icon" /> Compliance Radar</div>
                            {radarData.length > 0 ? (
                                <ResponsiveContainer width="100%" height={350}>
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="rgba(148,163,184,0.1)" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                        <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                                        <Radar name="Compliance" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} strokeWidth={2} />
                                    </RadarChart>
                                </ResponsiveContainer>
                            ) : <div style={{ height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>Insufficient data for risk radar.</div>}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
