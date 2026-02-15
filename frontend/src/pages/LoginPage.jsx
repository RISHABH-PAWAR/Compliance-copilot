import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { Shield, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { authApi } from '../api'

export default function LoginPage() {
    const [email, setEmail] = useState('hr@demo.com')
    const [password, setPassword] = useState('hr123')
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const res = await authApi.login({ email, password })
            login(res.data)
            navigate('/')
        } catch (err) {
            console.error('Login error:', err)
            if (err.response?.status === 401) {
                setError('Invalid email or password. Please use the default credentials below.')
            } else if (!err.response) {
                setError('Cannot connect to backend server. Please ensure it is running on port 8000.')
            } else {
                setError('An unexpected error occurred. Please try again.')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card animate-in">
                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                    <div style={{ width: 56, height: 56, background: 'linear-gradient(135deg, #6366f1, #06b6d4)', borderRadius: 14, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, marginBottom: 16, boxShadow: '0 0 40px rgba(99, 102, 241, 0.3)' }}>
                        ⚖️
                    </div>
                    <h1 style={{ background: 'linear-gradient(135deg, #6366f1, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        Compliance Copilot
                    </h1>
                    <p style={{ marginTop: 4 }}>Indian Labor Law Intelligence Platform</p>
                </div>

                {error && (
                    <div style={{ background: 'rgba(239,68,68,0.12)', color: '#ef4444', padding: '12px', borderRadius: 8, marginBottom: 20, fontSize: 13, display: 'flex', gap: 10, alignItems: 'center' }}>
                        <AlertCircle size={16} style={{ flexShrink: 0 }} />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Email Address</label>
                        <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="hr@demo.com" required />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <input className="form-input" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••" required />
                            <button type="button" onClick={() => setShowPw(!showPw)} style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>
                                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary btn-full" disabled={loading} style={{ marginTop: 8, height: 46 }}>
                        {loading ? 'Signing in...' : 'Sign In to Dashboard'}
                    </button>
                </form>

                <div style={{ marginTop: 24, padding: '14px', background: 'rgba(99, 102, 241, 0.06)', borderRadius: 10, border: '1px solid rgba(99, 102, 241, 0.1)' }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#818cf8', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>System Credentials</div>
                    <div style={{ fontSize: 12, color: '#94a3b8' }}>
                        <div><strong style={{ color: '#f1f5f9' }}>Default Login:</strong> hr@demo.com / hr123</div>
                    </div>
                    <p style={{ fontSize: 11, color: '#64748b', marginTop: 8 }}>
                        Note: The system resets to zero data for your fresh analysis session.
                    </p>
                </div>
            </div>
        </div>
    )
}
