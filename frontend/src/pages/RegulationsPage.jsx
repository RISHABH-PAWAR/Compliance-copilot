import React, { useState, useEffect } from 'react'
import { ScrollText, ChevronRight, ChevronDown, Clock, AlertCircle, Search, Info } from 'lucide-react'
import { regulationApi } from '../api'

export default function RegulationsPage() {
    const [regulations, setRegulations] = useState([])
    const [expanded, setExpanded] = useState(null)
    const [search, setSearch] = useState('')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [tab, setTab] = useState('rules')

    const fetchRegulations = async () => {
        try {
            setLoading(true)
            const response = await regulationApi.list()
            setRegulations(response.data.regulations || response.data || [])
            setError(null)
        } catch (err) {
            console.error('Failed to fetch regulations:', err)
            setError('Unable to load regulations library. Please check your internet connection or backend status.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchRegulations()
    }, [])

    const filtered = (Array.isArray(regulations) ? regulations : []).filter(r =>
        (r.act_name || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.category || '').toLowerCase().includes(search.toLowerCase())
    )

    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Accessing National Compliance Library...</div>

    if (error) return (
        <div style={{ padding: 40, textAlign: 'center' }}>
            <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: 16 }} />
            <div style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: 8 }}>Library Offline</div>
            <div style={{ color: '#94a3b8', fontSize: 14, maxWidth: 400, margin: '0 auto', marginBottom: 24 }}>{error}</div>
            <button className="btn btn-primary" onClick={fetchRegulations}>Reload Library</button>
        </div>
    )

    return (
        <div>
            {/* Search */}
            <div style={{ position: 'relative', marginBottom: 20 }}>
                <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input className="form-input" style={{ paddingLeft: 40 }} placeholder="Search regulations by name or category..." value={search} onChange={e => setSearch(e.target.value)} />
            </div>

            {/* Summary Bar */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div style={{ padding: '8px 16px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)', fontSize: 12 }}>
                    <span style={{ color: '#64748b' }}>Acts in Library:</span> <strong style={{ color: '#f1f5f9' }}>{regulations.length}</strong>
                </div>
            </div>

            {/* Regulation List */}
            <div className="item-list" style={{ gap: 12 }}>
                {filtered.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                        <Info size={32} style={{ color: '#64748b', margin: '0 auto 12px' }} />
                        <div style={{ color: '#f1f5f9', fontWeight: 600 }}>No Regulations Found</div>
                        <div style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Try searching for a different act or check back later.</div>
                    </div>
                ) : filtered.map((reg) => (
                    <div key={reg.id} className="card" style={{ padding: 0 }}>
                        <div style={{ padding: '16px 20px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 14 }} onClick={() => setExpanded(expanded === reg.id ? null : reg.id)}>
                            <div style={{ width: 42, height: 42, background: reg.severity === 'critical' ? 'rgba(239,68,68,0.12)' : reg.severity === 'high' ? 'rgba(249,115,22,0.12)' : 'rgba(234,179,8,0.12)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', color: reg.severity === 'critical' ? '#ef4444' : reg.severity === 'high' ? '#f97316' : '#eab308', flexShrink: 0 }}>
                                <ScrollText size={18} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>{reg.act_name}</div>
                                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                                    {reg.category} • {reg.rules?.length || 0} rules • States: {reg.states || 'All'}
                                    {reg.diffs?.length > 0 && <span style={{ color: '#eab308', marginLeft: 8 }}>🔄 {reg.diffs.length} recent change(s)</span>}
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                <div style={{ textAlign: 'right', fontSize: 11, color: '#64748b' }}>
                                    <div>Updated: {reg.last_updated || reg.lastUpdated || 'N/A'}</div>
                                </div>
                                <span className={`badge ${reg.severity}`}>{reg.severity}</span>
                                {expanded === reg.id ? <ChevronDown size={16} style={{ color: '#64748b' }} /> : <ChevronRight size={16} style={{ color: '#64748b' }} />}
                            </div>
                        </div>

                        {expanded === reg.id && (
                            <div style={{ borderTop: '1px solid var(--border-primary)', padding: '16px 20px' }}>
                                {/* Sub-tabs */}
                                <div style={{ display: 'flex', gap: 4, marginBottom: 16 }}>
                                    {[['rules', 'Rules'], ['diffs', `What Changed (${reg.diffs?.length || 0})`]].map(([k, l]) => (
                                        <button key={k} className={`btn ${tab === k ? 'btn-primary' : 'btn-ghost'}`} style={{ fontSize: 12, padding: '5px 12px' }} onClick={() => setTab(k)}>{l}</button>
                                    ))}
                                </div>

                                {tab === 'rules' && (
                                    <table className="data-table">
                                        <thead><tr><th>Section</th><th>Title</th><th>Requirement</th><th>Severity</th><th>Max Penalty</th></tr></thead>
                                        <tbody>
                                            {reg.rulesList?.length > 0 ? reg.rulesList.map((r, i) => (
                                                <tr key={i}>
                                                    <td style={{ fontWeight: 600, color: '#818cf8' }}>{r.section}</td>
                                                    <td style={{ color: '#f1f5f9' }}>{r.title}</td>
                                                    <td>{r.requirement}</td>
                                                    <td><span className={`badge ${r.severity}`}>{r.severity}</span></td>
                                                    <td style={{ color: '#f97316', fontWeight: 600 }}>{r.penalty}</td>
                                                </tr>
                                            )) : (
                                                <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b', padding: 20 }}>No specific rules documented yet.</td></tr>
                                            )}
                                        </tbody>
                                    </table>
                                )}

                                {tab === 'diffs' && (
                                    (reg.diffs?.length > 0) ? (
                                        <div className="item-list">
                                            {reg.diffs.map((d, i) => (
                                                <div className="list-item" key={i}>
                                                    <div className="item-icon" style={{ background: 'rgba(234,179,8,0.12)', color: '#eab308' }}>
                                                        <Clock size={14} />
                                                    </div>
                                                    <div className="item-content">
                                                        <div className="item-title" style={{ whiteSpace: 'normal' }}>{d.change}</div>
                                                        <div className="item-desc">{d.section} • {d.date} • Type: {d.type}</div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div style={{ textAlign: 'center', padding: 24, color: '#64748b', fontSize: 13 }}>No recent changes detected for this regulation</div>
                                    )
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
