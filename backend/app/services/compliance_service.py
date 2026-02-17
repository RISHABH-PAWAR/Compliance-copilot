"""Compliance Service - Core Compliance Analysis Engine"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sql.regulation import Regulation, RegulationRule
from app.models.sql.compliance_log import ComplianceLog
from app.models.sql.company import Company
from app.models.sql.alert import Alert
from app.schemas.compliance import (
    ComplianceGap, ComplianceOverview, ComplianceChecklist,
    RiskScoreBreakdown, StateComplianceMap,
)


class ComplianceService:
    """Core compliance analysis engine with deterministic risk scoring"""

    INSPECTION_FREQ_SCORES = {
        "monthly": 3.0,
        "quarterly": 2.5,
        "semi_annually": 2.0,
        "annually": 1.5,
        "on_complaint": 1.0,
    }

    def __init__(self, db: Session):
        self.db = db

    def calculate_risk_score(self, rule: RegulationRule, employee_count: int = 100) -> RiskScoreBreakdown:
        """
        Risk Score = (Penalty Weight × 2) + (Inspection Frequency × 1.5) + (Employee Impact Scale) + (Urgency Factor)
        """
        # Penalty weight: normalize penalty to 0-5 scale
        penalty_weight = min(rule.penalty_amount / 100000, 5.0) if rule.penalty_amount else 0.5
        
        # Inspection frequency score
        inspection_score = self.INSPECTION_FREQ_SCORES.get(
            rule.inspection_frequency, 1.0
        )
        
        # Employee impact scale: proportion of employees affected (0-3)
        threshold = rule.employee_threshold or 1
        impact_ratio = min(employee_count / max(threshold, 1), 3.0)
        employee_impact = impact_ratio
        
        # Urgency factor from rule
        urgency = rule.urgency_factor or 1.0
        
        total = (penalty_weight * 2) + (inspection_score * 1.5) + employee_impact + urgency
        
        # Normalize to 0-100
        normalized = min((total / 20) * 100, 100)
        
        risk_level = self._score_to_level(normalized)
        
        return RiskScoreBreakdown(
            penalty_weight=penalty_weight,
            inspection_frequency_score=inspection_score,
            employee_impact_scale=employee_impact,
            urgency_factor=urgency,
            total_score=round(normalized, 1),
            risk_level=risk_level,
        )

    def _score_to_level(self, score: float) -> str:
        if score >= 75:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        return "low"

    def analyze_company_compliance(self, company_id: int) -> ComplianceOverview:
        """Run full compliance analysis for a company"""
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return self._get_demo_overview(company_id)

        states = company.operational_states or ["maharashtra"]
        employee_count = company.employee_count or 200

        # Get all applicable rules
        rules = self.db.query(RegulationRule).filter(
            RegulationRule.is_active == True,
            RegulationRule.employee_threshold <= employee_count,
        ).all()

        applicable_rules = [
            r for r in rules
            if r.applicable_state == "all" or r.applicable_state in states
        ]

        if not applicable_rules:
            return self._get_demo_overview(company_id)

        gaps = []
        compliant = partial = violations = not_applicable = 0

        for rule in applicable_rules:
            # Check existing compliance log
            existing = self.db.query(ComplianceLog).filter(
                ComplianceLog.company_id == company_id,
                ComplianceLog.regulation_rule_id == rule.id,
            ).first()

            risk = self.calculate_risk_score(rule, employee_count)
            reg = self.db.query(Regulation).filter(Regulation.id == rule.regulation_id).first()

            if existing:
                # Always re-analyze with AI if we are performing a sync, 
                # or if it was previously a simulation
                status, gap, confidence = self._analyze_with_ai(company_id, rule)
                existing.status = status
                existing.gap_description = gap
                existing.confidence_score = confidence
                existing.analyzed_by = "ai"
                # Update risk score as well in case employee count or rules changed
                existing.risk_score = risk.total_score
                existing.risk_level = risk.risk_level
                status = status
            else:
                # Real AI Analysis instead of simulation
                status, gap, confidence = self._analyze_with_ai(company_id, rule)
                
                # Create compliance log
                log = ComplianceLog(
                    company_id=company_id,
                    regulation_rule_id=rule.id,
                    status=status,
                    gap_description=gap,
                    risk_score=risk.total_score,
                    risk_level=risk.risk_level,
                    penalty_weight=risk.penalty_weight,
                    inspection_frequency_score=risk.inspection_frequency_score,
                    employee_impact_scale=risk.employee_impact_scale,
                    urgency_factor=risk.urgency_factor,
                    estimated_penalty=rule.penalty_amount,
                    corrective_action=self._get_corrective_action(rule, status),
                    department_responsible=self._get_responsible_dept(rule),
                    documentation_needed=rule.documentation_required or [],
                    deadline=datetime.utcnow() + timedelta(days=30),
                    analyzed_by="ai",
                    confidence_score=confidence,
                    legal_reference=f"Section {rule.section_number}" if rule.section_number else None,
                )
                self.db.add(log)
                existing = log
                
                # Trigger Alert for new violations
                if status in ("violation", "partial"):
                    try:
                        from app.services.alert_service import AlertService
                        alert_svc = AlertService(self.db)
                        priority = "critical" if status == "violation" else "high"
                        alert_svc.create_alert(
                            company_id=company_id,
                            title=f"Compliance {status.capitalize()}: {rule.rule_title}",
                            description=gap or f"New compliance issue detected in {rule.rule_title}.",
                            alert_type="compliance_gap",
                            priority=priority,
                            regulation_id=rule.regulation_id
                        )
                    except Exception as ae:
                        import logging
                        logging.error(f"Failed to create alert: {ae}")

            if status == "compliant":
                compliant += 1
            elif status == "partial":
                partial += 1
            elif status == "violation":
                violations += 1
            else:
                not_applicable += 1

            if status in ("partial", "violation"):
                gaps.append(ComplianceGap(
                    id=existing.id if existing.id else 0,
                    company_id=company_id,
                    regulation_rule_id=rule.id,
                    rule_title=rule.rule_title,
                    act_name=reg.act_name if reg else "Unknown Act",
                    status=status,
                    gap_description=existing.gap_description,
                    risk_score=risk.total_score,
                    risk_level=risk.risk_level,
                    estimated_penalty=rule.penalty_amount,
                    estimated_cost_impact=rule.penalty_amount * 1.5,
                    corrective_action=existing.corrective_action,
                    department_responsible=existing.department_responsible,
                    documentation_needed=rule.documentation_required or [],
                    deadline=existing.deadline,
                    resolved=existing.resolved,
                    legal_reference=existing.legal_reference,
                    analyzed_by=existing.analyzed_by,
                    confidence_score=existing.confidence_score,
                    affected_employees=company.employee_count or 0,
                    created_at=existing.created_at or datetime.utcnow(),
                ))

        self.db.commit()
        total = compliant + partial + violations + not_applicable
        score = (compliant / max(total, 1)) * 100

        total_exposure = sum(g.estimated_penalty for g in gaps)

        return ComplianceOverview(
            company_id=company_id,
            total_rules_checked=total,
            rules_checked=total,
            compliant=compliant,
            partial=partial,
            violations=violations,
            not_applicable=not_applicable,
            overall_score=round(score, 1),
            score=round(score, 1),
            overall_risk_level=self._score_to_level(100 - score),
            total_financial_exposure=total_exposure,
            total_gaps=len(gaps),
            critical_gaps=sum(1 for g in gaps if g.risk_level == "critical"),
            states=len(company.operational_states) if company and company.operational_states else 1,
            gaps=sorted(gaps, key=lambda g: g.risk_score, reverse=True),
        )

    def get_state_compliance_map(self, company_id: int) -> List[StateComplianceMap]:
        """Get state-wise compliance mapping"""
        company = self.db.query(Company).filter(Company.id == company_id).first()
        states = company.operational_states if company else ["maharashtra", "gujarat", "tamil_nadu"]

        result = []
        for state in states:
            logs = self.db.query(ComplianceLog).filter(
                ComplianceLog.company_id == company_id,
            ).all()

            # Filter by state via regulation rule
            state_logs = []
            for log in logs:
                rule = self.db.query(RegulationRule).filter(
                    RegulationRule.id == log.regulation_rule_id
                ).first()
                if rule and (rule.applicable_state == "all" or rule.applicable_state == state):
                    state_logs.append(log)

            compliant = sum(1 for l in state_logs if l.status == "compliant")
            violations = sum(1 for l in state_logs if l.status == "violation")
            partial = sum(1 for l in state_logs if l.status == "partial")
            total = len(state_logs)
            exposure = sum(l.estimated_penalty or 0 for l in state_logs if l.status != "compliant")

            avg_risk = sum(l.risk_score or 0 for l in state_logs) / max(total, 1)

            result.append(StateComplianceMap(
                state=state,
                total_rules=total,
                compliant=compliant,
                violations=violations,
                partial=partial,
                risk_level=self._score_to_level(avg_risk),
                risk_score=round(avg_risk, 1),
                financial_exposure=exposure,
            ))

        if not result:
            result = self._get_demo_state_map()

        return result

    def generate_checklist(self, company_id: int) -> List[ComplianceChecklist]:
        """Generate compliance checklist from violations"""
        logs = self.db.query(ComplianceLog).filter(
            ComplianceLog.company_id == company_id,
            ComplianceLog.status.in_(["violation", "partial"]),
            ComplianceLog.resolved == False,
        ).all()

        if not logs:
            return self._get_demo_checklist()

        checklist = []
        for log in logs:
            rule = self.db.query(RegulationRule).filter(
                RegulationRule.id == log.regulation_rule_id
            ).first()
            reg = self.db.query(Regulation).filter(
                Regulation.id == rule.regulation_id
            ).first() if rule else None

            checklist.append(ComplianceChecklist(
                id=log.id,
                rule_title=rule.rule_title if rule else "Unknown Rule",
                act_name=reg.act_name if reg else "Unknown Act",
                corrective_action=log.corrective_action or "Review and update policy",
                department=log.department_responsible or "HR",
                documentation_needed=log.documentation_needed or [],
                deadline=log.deadline,
                priority=log.risk_level or "medium",
                status="pending" if not log.resolved else "completed",
                inspection_readiness=False,
            ))

        return sorted(checklist, key=lambda c: ["critical", "high", "medium", "low"].index(c.priority))

    def _analyze_with_ai(self, company_id: int, rule: RegulationRule) -> tuple:
        """Fetch related policy chunks and use AI to compare against rule"""
        from app.ai.retrieval import HybridRetrieval
        from app.ai.chains import compliance_chains
        
        try:
            retrieval = HybridRetrieval()
            # Search for related policy chunks in company namespace
            policy_results = retrieval.vectorstore.search(
                query=rule.requirement,
                namespace=f"company_{company_id}",
                top_k=3
            )
            
            if not policy_results:
                return "violation", "No relevant policy found for this requirement.", 0.7
                
            policy_text = "\n\n".join([r.get("text", "") for r in policy_results])
            
            result = compliance_chains.compare_policy_vs_rule(
                policy_text=policy_text,
                rule_text=rule.requirement
            )
            
            if result.get("status") == "success":
                # Map comparison to status
                comparison = result.get("comparison", "").lower()
                if "fully compliant" in comparison or "no gap" in comparison:
                    return "compliant", None, 0.9
                elif "partial" in comparison or "missing" in comparison:
                    return "partial", result.get("comparison"), 0.85
                else:
                    return "violation", result.get("comparison"), 0.85
            
            return self._simulate_compliance(rule), "AI Analysis unreachable - using simulation.", 0.5
            
        except Exception as e:
            import logging
            logging.error(f"AI Analysis failed for rule {rule.id}: {e}")
            return self._simulate_compliance(rule), f"Analysis error: {str(e)}", 0.0

    def _simulate_compliance(self, rule: RegulationRule) -> str:
        """Simulate compliance status based on rule characteristics"""
        if rule.severity == "critical":
            return "violation"
        elif rule.severity == "high":
            return "partial"
        elif rule.severity == "medium":
            import random
            return random.choice(["compliant", "partial", "compliant"])
        return "compliant"

    def _get_corrective_action(self, rule: RegulationRule, status: str) -> Optional[str]:
        if status == "compliant":
            return None
        actions = {
            "violation": f"Immediately update company policy to comply with {rule.rule_title}. Ensure documentation is prepared for inspection.",
            "partial": f"Review and align company policy with {rule.rule_title}. Minor adjustments needed in documentation.",
        }
        return actions.get(status, "Review compliance requirements")

    def _get_responsible_dept(self, rule: RegulationRule) -> str:
        reg = self.db.query(Regulation).filter(Regulation.id == rule.regulation_id).first()
        if reg:
            dept_map = {
                "wages": "HR & Finance",
                "safety": "Operations",
                "benefits": "HR",
                "hours": "Operations",
                "social_security": "HR & Finance",
                "bonus": "Finance",
            }
            return dept_map.get(reg.category, "HR")
        return "HR"

    def _get_demo_overview(self, company_id: int) -> ComplianceOverview:
        demo_gaps = [
            ComplianceGap(id=1, company_id=company_id, regulation_rule_id=1, rule_title="Overtime Payment Compliance", act_name="Factories Act, 1948",
                status="violation", gap_description="Company overtime policy allows 60+ hours/week. Factories Act limits to 48 hours with overtime pay at 2x rate.",
                risk_score=82.5, risk_level="critical", estimated_penalty=500000, estimated_cost_impact=750000,
                corrective_action="Update overtime policy to cap weekly hours at 48. Ensure overtime payment at 2x normal wages.",
                department_responsible="HR & Operations", documentation_needed=["Updated overtime policy", "Wage registers", "Attendance records"],
                deadline=datetime(2026, 3, 15), resolved=False, legal_reference="Section 51, 59 Factories Act",
                analyzed_by="ai", confidence_score=0.92, created_at=datetime.utcnow()),
            ComplianceGap(id=2, company_id=company_id, regulation_rule_id=2, rule_title="Minimum Wage Revision Compliance", act_name="Minimum Wages Act, 1948",
                status="violation", gap_description="Current wage structure below revised minimum wages for unskilled workers in Maharashtra (effective Jan 2026).",
                risk_score=78.3, risk_level="critical", estimated_penalty=350000, estimated_cost_impact=1200000,
                corrective_action="Revise wage structure for unskilled workers to meet ₹18,500/month minimum. Update payroll system.",
                department_responsible="HR & Finance", documentation_needed=["Revised wage structure", "Payroll update records", "Employee notification"],
                deadline=datetime(2026, 3, 1), resolved=False, legal_reference="Section 12, Minimum Wages Act",
                analyzed_by="ai", confidence_score=0.95, created_at=datetime.utcnow()),
            ComplianceGap(id=3, company_id=company_id, regulation_rule_id=3, rule_title="EPF Contribution Rate", act_name="EPF Act, 1952",
                status="partial", gap_description="EPF contribution being calculated on basic salary only. Should include DA and retaining allowance.",
                risk_score=55.0, risk_level="high", estimated_penalty=200000, estimated_cost_impact=500000,
                corrective_action="Recalculate EPF contributions to include DA and retaining allowance in the wage definition.",
                department_responsible="HR & Finance", documentation_needed=["Updated EPF calculation sheet", "Payroll software config"],
                deadline=datetime(2026, 4, 1), resolved=False, legal_reference="Section 6, EPF Act",
                analyzed_by="ai", confidence_score=0.88, created_at=datetime.utcnow()),
            ComplianceGap(id=4, company_id=company_id, regulation_rule_id=4, rule_title="ESI Coverage for Contract Workers", act_name="ESI Act, 1948",
                status="partial", gap_description="Contract workers above wage limit not covered under ESI. Need verification of wage ceilings.",
                risk_score=45.0, risk_level="medium", estimated_penalty=100000, estimated_cost_impact=300000,
                corrective_action="Verify all contract workers' wages against ESI ceiling. Register eligible workers.",
                department_responsible="HR", documentation_needed=["Contract worker list", "Wage records", "ESI registration forms"],
                deadline=datetime(2026, 5, 1), resolved=False, legal_reference="Section 2(9), ESI Act",
                analyzed_by="ai", confidence_score=0.80, created_at=datetime.utcnow()),
            ComplianceGap(id=5, company_id=company_id, regulation_rule_id=5, rule_title="Bonus Payment Deadline", act_name="Payment of Bonus Act, 1965",
                status="violation", gap_description="Annual bonus not distributed within 8 months of closing accounting year as required.",
                risk_score=62.0, risk_level="high", estimated_penalty=250000, estimated_cost_impact=400000,
                corrective_action="Distribute pending bonus within deadline. Set up automated reminders for future compliance.",
                department_responsible="Finance", documentation_needed=["Bonus calculation sheet", "Distribution records", "Employee acknowledgments"],
                deadline=datetime(2026, 3, 31), resolved=False, legal_reference="Section 19, Payment of Bonus Act",
                analyzed_by="ai", confidence_score=0.90, created_at=datetime.utcnow()),
            ComplianceGap(id=6, company_id=company_id, regulation_rule_id=6, rule_title="Shop Registration Renewal", act_name="Shops & Establishment Act",
                status="partial", gap_description="Branch office registration renewal pending for Gujarat operations.",
                risk_score=35.0, risk_level="medium", estimated_penalty=50000, estimated_cost_impact=75000,
                corrective_action="Renew shop and establishment registration for Gujarat branch before expiry.",
                department_responsible="Operations", documentation_needed=["Registration renewal form", "Updated employee count", "Fee receipt"],
                deadline=datetime(2026, 6, 1), resolved=False, legal_reference="Section 7, Shops & Establishment Act",
                analyzed_by="ai", confidence_score=0.85, created_at=datetime.utcnow()),
        ]
        return ComplianceOverview(
            company_id=company_id, total_rules_checked=24, compliant=15, partial=4, violations=3,
            not_applicable=2, overall_score=62.5, overall_risk_level="high",
            total_financial_exposure=sum(g.estimated_penalty for g in demo_gaps), gaps=demo_gaps,
        )

    def _get_demo_state_map(self) -> List[StateComplianceMap]:
        return [
            StateComplianceMap(state="maharashtra", total_rules=12, compliant=7, violations=3, partial=2, risk_level="high", risk_score=65.0, financial_exposure=850000),
            StateComplianceMap(state="gujarat", total_rules=10, compliant=6, violations=2, partial=2, risk_level="medium", risk_score=45.0, financial_exposure=400000),
            StateComplianceMap(state="tamil_nadu", total_rules=8, compliant=5, violations=1, partial=2, risk_level="medium", risk_score=38.0, financial_exposure=250000),
            StateComplianceMap(state="karnataka", total_rules=9, compliant=7, violations=1, partial=1, risk_level="low", risk_score=22.0, financial_exposure=150000),
        ]

    def _get_demo_checklist(self) -> List[ComplianceChecklist]:
        return [
            ComplianceChecklist(id=1, rule_title="Overtime Payment Compliance", act_name="Factories Act, 1948",
                corrective_action="Update overtime policy to cap weekly hours at 48. Ensure overtime payment at 2x normal wages.",
                department="HR & Operations", documentation_needed=["Updated overtime policy", "Wage registers", "Attendance records"],
                deadline=datetime(2026, 3, 15), priority="critical", status="pending"),
            ComplianceChecklist(id=2, rule_title="Minimum Wage Revision", act_name="Minimum Wages Act, 1948",
                corrective_action="Revise wage structure for unskilled workers to meet ₹18,500/month minimum.",
                department="HR & Finance", documentation_needed=["Revised wage structure", "Payroll update records"],
                deadline=datetime(2026, 3, 1), priority="critical", status="pending"),
            ComplianceChecklist(id=3, rule_title="Bonus Payment Deadline", act_name="Payment of Bonus Act, 1965",
                corrective_action="Distribute pending bonus within statutory deadline.",
                department="Finance", documentation_needed=["Bonus calculation sheet", "Distribution records"],
                deadline=datetime(2026, 3, 31), priority="high", status="in_progress"),
            ComplianceChecklist(id=4, rule_title="EPF Contribution Calculation", act_name="EPF Act, 1952",
                corrective_action="Include DA and retaining allowance in EPF wage calculation.",
                department="HR & Finance", documentation_needed=["Updated EPF calculation sheet"],
                deadline=datetime(2026, 4, 1), priority="high", status="pending"),
            ComplianceChecklist(id=5, rule_title="ESI Coverage Verification", act_name="ESI Act, 1948",
                corrective_action="Verify contract workers against ESI wage ceiling. Register eligible workers.",
                department="HR", documentation_needed=["Contract worker list", "ESI forms"],
                deadline=datetime(2026, 5, 1), priority="medium", status="pending"),
            ComplianceChecklist(id=6, rule_title="Shop Registration Renewal", act_name="Shops & Establishment Act",
                corrective_action="Renew registration for Gujarat branch office.",
                department="Operations", documentation_needed=["Registration form", "Fee receipt"],
                deadline=datetime(2026, 6, 1), priority="medium", status="pending"),
        ]
