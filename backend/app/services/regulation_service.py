"""Regulation Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.sql.regulation import Regulation, RegulationRule
from app.schemas.regulation import RegulationCreate, RegulationRuleCreate, RegulationDiff


class RegulationService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, state: Optional[str] = None, category: Optional[str] = None) -> List[Regulation]:
        query = self.db.query(Regulation).filter(Regulation.is_active == True)
        if category:
            query = query.filter(Regulation.category == category)
        regulations = query.all()
        
        if state:
            regulations = [
                r for r in regulations
                if "all" in (r.applicable_states or []) or state in (r.applicable_states or [])
            ]
        return regulations

    def get_by_id(self, regulation_id: int) -> Regulation:
        reg = self.db.query(Regulation).filter(Regulation.id == regulation_id).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Regulation not found")
        return reg

    def get_rules(self, regulation_id: int, state: Optional[str] = None) -> List[RegulationRule]:
        query = self.db.query(RegulationRule).filter(
            RegulationRule.regulation_id == regulation_id,
            RegulationRule.is_active == True,
        )
        if state:
            query = query.filter(
                (RegulationRule.applicable_state == "all") |
                (RegulationRule.applicable_state == state)
            )
        return query.all()

    def get_rules_for_company(self, company_states: List[str], employee_count: int) -> List[RegulationRule]:
        """Get all applicable rules for a company based on states and size"""
        rules = self.db.query(RegulationRule).filter(
            RegulationRule.is_active == True,
            RegulationRule.employee_threshold <= employee_count,
        ).all()
        
        applicable = []
        for rule in rules:
            if rule.applicable_state == "all" or rule.applicable_state in company_states:
                applicable.append(rule)
        return applicable

    def create_regulation(self, data: RegulationCreate) -> Regulation:
        reg = Regulation(**data.model_dump())
        self.db.add(reg)
        self.db.commit()
        self.db.refresh(reg)
        return reg

    def create_rule(self, data: RegulationRuleCreate) -> RegulationRule:
        rule = RegulationRule(**data.model_dump())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_diffs(self, regulation_id: int) -> List[RegulationDiff]:
        """Get regulatory changes (What Changed?) for a regulation"""
        rules = self.db.query(RegulationRule).filter(
            RegulationRule.regulation_id == regulation_id,
            RegulationRule.previous_version_id.isnot(None),
        ).all()

        diffs = []
        for rule in rules:
            prev = self.db.query(RegulationRule).filter(
                RegulationRule.id == rule.previous_version_id
            ).first()
            if prev:
                if prev.penalty_amount != rule.penalty_amount:
                    diffs.append(RegulationDiff(
                        rule_id=rule.id,
                        rule_title=rule.rule_title,
                        field="penalty_amount",
                        old_value=f"₹{prev.penalty_amount:,.0f}",
                        new_value=f"₹{rule.penalty_amount:,.0f}",
                        change_date=rule.updated_at or rule.created_at,
                        affected_departments=["HR", "Finance"],
                        estimated_cost_impact=rule.penalty_amount - prev.penalty_amount,
                    ))
                if prev.requirement != rule.requirement:
                    diffs.append(RegulationDiff(
                        rule_id=rule.id,
                        rule_title=rule.rule_title,
                        field="requirement",
                        old_value=prev.requirement[:200],
                        new_value=rule.requirement[:200],
                        change_date=rule.updated_at or rule.created_at,
                        affected_departments=["HR", "Operations"],
                    ))
        return diffs
