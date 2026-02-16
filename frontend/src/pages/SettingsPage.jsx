import React from 'react'
import { useAuth } from '../App'
import { User, Building, Shield, Bell, Key, Globe } from 'lucide-react'

export default function SettingsPage() {
    const { user } = useAuth()

    const sections = [
        {
            icon: User, title: 'Profile', description: 'Manage your account details', fields: [
                { label: 'Full Name', value: user?.name || 'HR Admin', type: 'text' },
                { label: 'Email', value: user?.email || 'hr@demo.com', type: 'email' },
                { label: 'Role', value: user?.role?.replace('_', ' ') || 'HR Admin', type: 'text', disabled: true },
            ]
        },
        {
            icon: Building, title: 'Company', description: 'Organization settings', fields: [
                { label: 'Company Name', value: 'Demo Manufacturing Pvt Ltd', type: 'text' },
                { label: 'Industry', value: 'Manufacturing', type: 'text' },
                { label: 'Employee Count', value: '450', type: 'number' },
                { label: 'Operational States', value: 'MH, GJ, KA', type: 'text' },
                { label: 'GSTIN', value: '27AAACR5055K1Z5', type: 'text' },
            ]
        },
        {
            icon: Shield, title: 'Subscription', description: 'Current plan and billing', fields: [
                { label: 'Plan', value: 'Professional', type: 'text', disabled: true },
                { label: 'Price', value: '₹50,000/month', type: 'text', disabled: true },
                { label: 'Max States', value: '3', type: 'text', disabled: true },
                { label: 'Max Users', value: '15', type: 'text', disabled: true },
            ]
        },
    ]

    return (
        <div style={{ maxWidth: 700 }}>
            {sections.map((section, i) => (
                <div key={i} className="card" style={{ marginBottom: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
                        <div style={{ width: 38, height: 38, background: 'rgba(99,102,241,0.1)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8' }}>
                            <section.icon size={18} />
                        </div>
                        <div>
                            <div style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9' }}>{section.title}</div>
                            <div style={{ fontSize: 12, color: '#64748b' }}>{section.description}</div>
                        </div>
                    </div>
                    {section.fields.map((field, j) => (
                        <div className="form-group" key={j}>
                            <label className="form-label">{field.label}</label>
                            <input className="form-input" type={field.type} defaultValue={field.value} disabled={field.disabled} style={field.disabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}} />
                        </div>
                    ))}
                    <button className="btn btn-primary" style={{ marginTop: 8 }}>Save Changes</button>
                </div>
            ))}
        </div>
    )
}
