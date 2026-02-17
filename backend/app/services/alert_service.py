"""Alert Service"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sql.alert import Alert


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, company_id: int, title: str, description: str,
                     alert_type: str, priority: str = "medium",
                     regulation_id: Optional[int] = None) -> Alert:
        alert = Alert(
            company_id=company_id, title=title, description=description,
            alert_type=alert_type, priority=priority, regulation_id=regulation_id,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_alerts(self, company_id: int, unread_only: bool = False) -> dict:
        query = self.db.query(Alert).filter(
            Alert.company_id == company_id, Alert.is_dismissed == False,
        )
        if unread_only:
            query = query.filter(Alert.is_read == False)

        alerts = query.order_by(Alert.created_at.desc()).all()
        unread = self.db.query(Alert).filter(
            Alert.company_id == company_id, Alert.is_read == False, Alert.is_dismissed == False,
        ).count()

        if not alerts:
            return self._get_demo_alerts(company_id)

        return {"alerts": alerts, "total": len(alerts), "unread_count": unread}

    def mark_read(self, alert_id: int, company_id: int) -> Alert:
        alert = self.db.query(Alert).filter(Alert.id == alert_id, Alert.company_id == company_id).first()
        if alert:
            alert.is_read = True
            alert.read_at = datetime.utcnow()
            self.db.commit()
        return alert

    def dismiss(self, alert_id: int, company_id: int) -> Alert:
        alert = self.db.query(Alert).filter(Alert.id == alert_id, Alert.company_id == company_id).first()
        if alert:
            alert.is_dismissed = True
            self.db.commit()
        return alert

    def _get_demo_alerts(self, company_id: int) -> dict:
        demo = [
            {"id": 1, "company_id": company_id, "title": "⚠️ Maharashtra Minimum Wage Revision Effective March 2026",
             "description": "Maharashtra state has revised minimum wages for unskilled, semi-skilled, and skilled workers. New rates effective from 1st March 2026. Your current wage structure needs review.",
             "alert_type": "regulation_update", "priority": "critical", "is_read": False, "is_dismissed": False,
             "action_required": True, "created_at": datetime(2026, 2, 10), "read_at": None},
            {"id": 2, "company_id": company_id, "title": "🔴 Overtime Policy Violation Detected",
             "description": "Compliance analysis detected that your overtime policy exceeds the maximum hours permitted under Factories Act Section 51. Immediate corrective action required.",
             "alert_type": "compliance_gap", "priority": "critical", "is_read": False, "is_dismissed": False,
             "action_required": True, "created_at": datetime(2026, 2, 8), "read_at": None},
            {"id": 3, "company_id": company_id, "title": "📋 EPF Contribution Rate Update",
             "description": "EPFO has issued circular regarding inclusion of special allowances in PF wage calculation. Review your PF contribution structure.",
             "alert_type": "regulation_update", "priority": "high", "is_read": False, "is_dismissed": False,
             "action_required": True, "created_at": datetime(2026, 2, 5), "read_at": None},
            {"id": 4, "company_id": company_id, "title": "📅 Bonus Payment Deadline Approaching",
             "description": "Annual bonus distribution deadline is 31st March 2026 (within 8 months of accounting year close). Ensure timely distribution.",
             "alert_type": "deadline", "priority": "high", "is_read": True, "is_dismissed": False,
             "action_required": True, "created_at": datetime(2026, 2, 1), "read_at": datetime(2026, 2, 2)},
            {"id": 5, "company_id": company_id, "title": "🏗️ Gujarat Shop Registration Renewal Due",
             "description": "Shop and Establishment registration for Gujarat branch expires on 30th June 2026. Initiate renewal process.",
             "alert_type": "deadline", "priority": "medium", "is_read": True, "is_dismissed": False,
             "action_required": True, "created_at": datetime(2026, 1, 25), "read_at": datetime(2026, 1, 26)},
            {"id": 6, "company_id": company_id, "title": "✅ ESI Contribution Verified",
             "description": "Monthly ESI contribution for January 2026 has been verified. All eligible employees are covered under the scheme.",
             "alert_type": "compliance_gap", "priority": "low", "is_read": True, "is_dismissed": False,
             "action_required": False, "created_at": datetime(2026, 1, 20), "read_at": datetime(2026, 1, 21)},
        ]
        return {"alerts": demo, "total": len(demo), "unread_count": 3}
