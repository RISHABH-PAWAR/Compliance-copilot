import React, { useState, useEffect } from 'react'
import { FileText, Upload, Search, Clock, Eye, AlertCircle, CheckCircle2 } from 'lucide-react'
import { policyApi } from '../api'
import { Trash2, Edit2 } from 'lucide-react'

const typeLabels = {
    hr_manual: 'HR Manual',
    overtime_leave: 'Overtime/Leave',
    wages: 'Wages',
    social_security: 'Social Security',
    safety: 'Safety',
    handbook: 'Employee Handbook',
    attendance: 'Attendance Policy',
    leave_policy: 'Leave Policy'
}

export default function PoliciesPage() {
    const [policies, setPolicies] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [showUpload, setShowUpload] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(null)

    const fetchPolicies = async () => {
        try {
            setLoading(true)
            const response = await policyApi.list()
            setPolicies(response.data.policies || [])
            setError(null)
        } catch (err) {
            console.error('Failed to fetch policies:', err)
            setError('Failed to load policies. Please check if the backend is running.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPolicies()
    }, [])

    const handleFileUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append('file', file)
        formData.append('policy_type', 'hr_manual') // Default, user could select this in a real app
        formData.append('state', 'all')
        formData.append('department', 'HR')

        try {
            setUploading(true)
            setError(null)
            setSuccess(null)
            await policyApi.upload(formData)
            setSuccess(`Successfully uploaded ${file.name}`)
            setShowUpload(false)
            fetchPolicies() // Refresh list
        } catch (err) {
            console.error('Upload failed:', err)
            setError('Upload failed. Please try again.')
        } finally {
            setUploading(false)
            // Clear success message after 5 seconds
            setTimeout(() => setSuccess(null), 5000)
        }
    }

    const handleDelete = async (id, name) => {
        if (!window.confirm(`Are you sure you want to delete ${name}? This will also remove all associated compliance data.`)) return
        try {
            await policyApi.delete(id)
            setSuccess(`Deleted ${name}`)
            fetchPolicies()
        } catch (err) {
            console.error('Delete failed:', err)
            setError('Failed to delete policy.')
        }
    }

    const handleRename = async (id, oldName) => {
        const newName = window.prompt('Enter new filename:', oldName)
        if (!newName || newName === oldName) return
        try {
            await policyApi.update(id, { filename: newName })
            setSuccess(`Renamed to ${newName}`)
            fetchPolicies()
        } catch (err) {
            console.error('Rename failed:', err)
            setError('Failed to rename policy.')
        }
    }

    const filtered = policies.filter(p =>
        (p.name || p.filename || '').toLowerCase().includes(search.toLowerCase())
    )

    const formatSize = (bytes) => {
        if (!bytes) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    return (
        <div>
            <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                    <input className="form-input" style={{ paddingLeft: 40 }} placeholder="Search policies..." value={search} onChange={e => setSearch(e.target.value)} />
                </div>
                <button className="btn btn-primary" onClick={() => setShowUpload(!showUpload)}>
                    <Upload size={14} /> Upload Policy
                </button>
            </div>

            {error && (
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#f87171', padding: '12px 16px', borderRadius: 8, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <AlertCircle size={18} />
                    <span style={{ fontSize: 13 }}>{error}</span>
                </div>
            )}

            {success && (
                <div style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.2)', color: '#4ade80', padding: '12px 16px', borderRadius: 8, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <CheckCircle2 size={18} />
                    <span style={{ fontSize: 13 }}>{success}</span>
                </div>
            )}

            {showUpload && (
                <div className="card" style={{ marginBottom: 20, border: '1px dashed rgba(99,102,241,0.3)' }}>
                    <div style={{ textAlign: 'center', padding: 32 }}>
                        <Upload size={32} style={{ color: '#818cf8', marginBottom: 12 }} />
                        <div style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9', marginBottom: 4 }}>
                            {uploading ? 'Uploading...' : 'Choose a file to upload'}
                        </div>
                        <div style={{ fontSize: 12, color: '#64748b' }}>Supported: PDF, DOCX, TXT (Max 50MB)</div>
                        <input type="file" accept=".pdf,.docx,.txt" style={{ display: 'none' }} id="fileUpload" onChange={handleFileUpload} disabled={uploading} />
                        <label htmlFor="fileUpload" className={`btn ${uploading ? 'btn-ghost' : 'btn-secondary'}`} style={{ marginTop: 16, cursor: uploading ? 'default' : 'pointer' }}>
                            {uploading ? 'Please wait...' : 'Choose File'}
                        </label>
                    </div>
                </div>
            )}

            <div className="card" style={{ padding: 0 }}>
                {loading ? (
                    <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading policies...</div>
                ) : (
                    <table className="data-table">
                        <thead><tr><th>Document</th><th>Type</th><th>State</th><th>Size</th><th>Uploaded</th><th>Status</th><th></th></tr></thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="7" style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>No policies found. Upload your first policy!</td></tr>
                            ) : filtered.map((p) => (
                                <tr key={p.id}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                            <div style={{ width: 34, height: 34, background: 'rgba(99,102,241,0.1)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8', flexShrink: 0 }}>
                                                <FileText size={16} />
                                            </div>
                                            <div>
                                                <div style={{ color: '#f1f5f9', fontWeight: 600, fontSize: 13 }}>{p.name || p.filename}</div>
                                                <div style={{ fontSize: 11, color: '#64748b' }}>{p.file_type?.toUpperCase()} • {p.chunk_count || 0} chunks</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span className="badge info">{typeLabels[p.policy_type] || p.policy_type}</span></td>
                                    <td style={{ color: '#f1f5f9' }}>{p.state === 'all' ? 'All States' : p.state}</td>
                                    <td>{formatSize(p.file_size)}</td>
                                    <td>
                                        <div style={{ fontSize: 12 }}>{new Date(p.created_at).toLocaleDateString()}</div>
                                        <div style={{ fontSize: 11, color: '#64748b' }}>{p.uploaded_by_name || 'System User'}</div>
                                    </td>
                                    <td>
                                        <span className={`badge ${p.status === 'processed' ? 'low' : 'medium'}`}>
                                            {p.status === 'processed' ? '✓ Analyzed' : '⏳ Pending'}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: 4 }}>
                                            <button className="btn btn-ghost" style={{ padding: 4 }} title="View"><Eye size={14} /></button>
                                            <button className="btn btn-ghost" style={{ padding: 4, color: '#818cf8' }} title="Rename" onClick={() => handleRename(p.id, p.name || p.filename)}><Edit2 size={14} /></button>
                                            <button className="btn btn-ghost" style={{ padding: 4, color: '#f87171' }} title="Delete" onClick={() => handleDelete(p.id, p.name || p.filename)}><Trash2 size={14} /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}
