import React, { useState, useEffect } from 'react'
import { BarChart3, Download, FileText, Shield, DollarSign, Briefcase, Info, AlertTriangle } from 'lucide-react'
import { reportApi, API_BASE, downloadFile } from '../api'

const REPORT_TYPES = [
    { id: 'compliance_summary', name: 'Compliance Summary Report', icon: Shield, description: 'Overview of all compliance gaps, risk scores, and status across regulations', color: '#6366f1' },
    { id: 'risk_assessment', name: 'Risk Assessment Report', icon: BarChart3, description: 'Detailed risk scores, threat analysis, and mitigation recommendations', color: '#f97316' },
    { id: 'audit_pack', name: 'Audit Pack', icon: Briefcase, description: 'Complete audit documentation package with evidence and compliance logs', color: '#06b6d4' },
    { id: 'financial_exposure', name: 'Financial Exposure Report', icon: DollarSign, description: 'Penalty and cost impact analysis for CFO and finance teams', color: '#22c55e' },
]

export default function ReportsPage() {
    const [generating, setGenerating] = useState(null)
    const [generated, setGenerated] = useState(null)
    const [recentReports, setRecentReports] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchReports = async () => {
        try {
            setLoading(true)
            const response = await reportApi.list()
            setRecentReports(response.data.reports || response.data || [])
            setError(null)
        } catch (err) {
            console.error('Failed to fetch reports:', err)
            // Silence error for now as backend might not have this endpoint yet or return 404
            setRecentReports([])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchReports()
    }, [])

    const generate = async (type, e) => {
        if (e) e.preventDefault();
        console.log(`Generating report for type: ${type}`);
        setGenerating(type)
        try {
            const response = await reportApi.generate({ report_type: type })
            console.log('Generation response:', response.data);
            setGenerated(type)
            await fetchReports()
            // Optional: Auto-download on generation
            if (response.data?.download_url) {
                // Remove /api/v1 from download_url if it's already there to avoid double nesting
                const cleanUrl = response.data.download_url.replace('/api/v1', '')
                downloadFile(cleanUrl, `${type}_report.pdf`)
            }
            setTimeout(() => setGenerated(null), 3000)
        } catch (err) {
            console.error('Report generation failed:', err)
            alert(`Failed to generate report: ${err.message || 'Unknown error'}`)
        } finally {
            setGenerating(null)
        }
    }

    const handleDownload = async (reportId, e) => {
        if (e) e.preventDefault();
        console.log(`Downloading report: ${reportId}`);
        try {
            await downloadFile(`/reports/download/${reportId}`, `report_${reportId}.pdf`)
            console.log('Download triggered successfully');
        } catch (err) {
            console.error('Download failed:', err);
            alert(`Download failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
        }
    }

    return (
        <div>
            {/* Report Types */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 28 }}>
                {REPORT_TYPES.map((rt) => (
                    <div key={rt.id} className="card" style={{ padding: '24px 20px' }}>
                        <div style={{ width: 44, height: 44, background: `${rt.color}15`, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', color: rt.color, marginBottom: 14 }}>
                            <rt.icon size={20} />
                        </div>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9', marginBottom: 6 }}>{rt.name}</div>
                        <div style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.5, marginBottom: 16, minHeight: 36 }}>{rt.description}</div>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <button className="btn btn-primary" style={{ flex: 1 }} onClick={(e) => generate(rt.id, e)} disabled={generating === rt.id}>
                                {generating === rt.id ? '⏳ Generating...' : generated === rt.id ? '✅ Ready!' : '📄 Generate PDF'}
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={(e) => generate(rt.id, e)}
                                disabled={generating === rt.id}
                            >
                                <Download size={14} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Reports */}
            <div className="card">
                <div className="card-title"><FileText size={14} className="icon" /> Recent Reports</div>
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', color: '#64748b' }}>Loading history...</div>
                ) : recentReports.length > 0 ? (
                    <table className="data-table">
                        <thead><tr><th>Report</th><th>Format</th><th>Generated</th><th>Size</th><th></th></tr></thead>
                        <tbody>
                            {recentReports.map((r, i) => (
                                <tr key={i}>
                                    <td style={{ color: '#f1f5f9', fontWeight: 500 }}>{r.name}</td>
                                    <td><span className="badge info">{r.format || 'PDF'}</span></td>
                                    <td style={{ fontSize: 12 }}>{r.date || r.created_at}</td>
                                    <td style={{ fontSize: 12 }}>{r.size || 'N/A'}</td>
                                    <td><button className="btn btn-ghost" onClick={(e) => handleDownload(r.id, e)}><Download size={14} /> Download</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                        <Info size={24} style={{ color: '#64748b', margin: '0 auto 12px' }} />
                        <div style={{ color: '#f1f5f9', fontSize: 14 }}>No reports generated yet.</div>
                        <p style={{ color: '#64748b', fontSize: 12, marginTop: 4 }}>Use the cards above to generate your first analysis report.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
