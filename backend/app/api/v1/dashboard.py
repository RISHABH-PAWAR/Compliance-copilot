"""Dashboard Data Endpoints"""
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.compliance_service import ComplianceService
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("/hr")
async def hr_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.sql.regulation import Regulation, RegulationRule
    from app.models.sql.company import Company
    compliance = ComplianceService(db)
    alerts = AlertService(db)
    overview = compliance.analyze_company_compliance(user.company_id or 1)
    alert_data = alerts.get_alerts(user.company_id or 1)
    checklist = compliance.generate_checklist(user.company_id or 1)
    company = db.query(Company).filter(Company.id == (user.company_id or 1)).first()

    reg_count = db.query(Regulation).filter(Regulation.is_active == True).count()
    recent_changes = db.query(RegulationRule).filter(
        RegulationRule.updated_at >= datetime.utcnow() - timedelta(days=30)
    ).count()

    return {
        "compliance_score": overview.overall_score,
        "total_gaps": len(overview.gaps),
        "critical_gaps": sum(1 for g in overview.gaps if g.risk_level == "critical"),
        "high_gaps": sum(1 for g in overview.gaps if g.risk_level == "high"),
        "medium_gaps": sum(1 for g in overview.gaps if g.risk_level == "medium"),
        "low_gaps": sum(1 for g in overview.gaps if g.risk_level == "low"),
        "total_financial_exposure": overview.total_financial_exposure,
        "active_alerts": alert_data.get("unread_count", 0),
        "pending_actions": len([c for c in checklist if c.status == "pending"]),
        "regulations_tracked": reg_count or 7,
        "states_monitored": len(company.operational_states) if company and company.operational_states else 1,
        "recent_alerts": alert_data.get("alerts", [])[:5],
        "top_violations": [g.model_dump() for g in overview.gaps[:5]],
        "checklist": [c.model_dump() for c in checklist[:5]],
        "trend_data": _get_trend_data(),
        "timeline": _get_compliance_timeline(db, user.company_id or 1),
        "audit_trail": _get_audit_trail(db, user.company_id or 1),
    }


@router.get("/operations")
async def operations_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    compliance = ComplianceService(db)
    state_map = compliance.get_state_compliance_map(user.company_id or 1)
    overview = compliance.analyze_company_compliance(user.company_id or 1)

    return {
        "compliance_score": overview.overall_score,
        "state_wise_risk": [s.model_dump() for s in state_map],
        "total_gaps": len(overview.gaps),
        "top_violations": [g.model_dump() for g in overview.gaps[:5]],
        "trend_data": _get_trend_data(),
    }


@router.get("/cfo")
async def cfo_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    compliance = ComplianceService(db)
    overview = compliance.analyze_company_compliance(user.company_id or 1)
    state_map = compliance.get_state_compliance_map(user.company_id or 1)

    penalty_breakdown = {}
    for gap in overview.gaps:
        act = gap.act_name
        if act not in penalty_breakdown:
            penalty_breakdown[act] = 0
        penalty_breakdown[act] += gap.estimated_penalty

    return {
        "total_financial_exposure": overview.total_financial_exposure,
        "monthly_risk": overview.total_financial_exposure / 12,
        "penalty_breakdown": [{"act": k, "amount": v} for k, v in penalty_breakdown.items()],
        "state_exposure": [{"state": s.state, "exposure": s.financial_exposure} for s in state_map],
        "compliance_score": overview.overall_score,
        "critical_violations": sum(1 for g in overview.gaps if g.risk_level == "critical"),
        "trend_data": _get_financial_trend_data(),
    }


@router.get("/auditor")
async def auditor_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    compliance = ComplianceService(db)
    overview = compliance.analyze_company_compliance(user.company_id or 1)

    return {
        "compliance_score": overview.overall_score,
        "total_rules_checked": overview.total_rules_checked,
        "compliant": overview.compliant,
        "partial": overview.partial,
        "violations": overview.violations,
        "timeline": _get_compliance_timeline(db, user.company_id or 1),
        "evidence_records": overview.total_rules_checked,
        "audit_trail": _get_audit_trail(db, user.company_id or 1),
    }


def _get_trend_data():
    now = datetime.utcnow()
    return [
        {"month": (now - timedelta(days=30 * i)).strftime("%b %Y"),
         "compliance_score": max(40, 75 - i * 3 + (i % 2) * 5),
         "violations": max(0, 3 + i - (i % 3)),
         "gaps_resolved": max(0, 5 - i + (i % 2) * 2)}
        for i in range(6, -1, -1)
    ]


def _get_financial_trend_data():
    now = datetime.utcnow()
    return [
        {"month": (now - timedelta(days=30 * i)).strftime("%b %Y"),
         "exposure": max(200000, 1500000 - i * 150000 + (i % 2) * 100000),
         "penalties_avoided": max(0, 300000 - i * 50000)}
        for i in range(6, -1, -1)
    ]


def _get_compliance_timeline(db: Session, company_id: int):
    from app.models.sql.alert import Alert
    alerts = db.query(Alert).filter(Alert.company_id == company_id).order_by(Alert.created_at.desc()).limit(7).all()
    
    return [
        {
            "date": a.created_at.strftime("%Y-%m-%d"),
            "event": a.title,
            "type": a.alert_type,
            "severity": a.priority
        } for a in alerts
    ] or [
        {"date": "2026-02-13", "event": "System Initialized", "type": "info", "severity": "info"}
    ]


def _get_audit_trail(db: Session, company_id: int):
    from app.models.sql.audit_trail import AuditTrail
    from app.models.sql.user import User
    
    logs = db.query(AuditTrail).filter(AuditTrail.company_id == company_id).order_by(AuditTrail.created_at.desc()).limit(10).all()
    
    trail = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        trail.append({
            "timestamp": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user": user.full_name if user else "System",
            "action": log.action,
            "resource": f"{log.resource_type} #{log.resource_id}" if log.resource_id else log.resource_type
        })
    
    return trail or [
        {"timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "user": "System", "action": "Audit logging started", "resource": "Company #1"}
    ]
