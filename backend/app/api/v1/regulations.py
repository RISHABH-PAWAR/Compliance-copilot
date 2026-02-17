"""Regulation Endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.regulation_service import RegulationService
from app.schemas.regulation import RegulationResponse, RegulationRuleResponse, RegulationDiff

router = APIRouter()


@router.get("")
async def list_regulations(
    state: Optional[str] = None, category: Optional[str] = None,
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    service = RegulationService(db)
    regs = service.get_all(state, category)
    
    result = []
    for r in regs:
        # Calculate max severity from rules
        severities = [rule.severity for rule in r.rules]
        max_severity = "medium"
        if "critical" in severities: max_severity = "critical"
        elif "high" in severities: max_severity = "high"
        
        result.append({
            "id": r.id, 
            "act_name": r.act_name, 
            "act_code": r.act_code,
            "category": r.category, 
            "description": r.description,
            "applicable_states": r.applicable_states, 
            "applicable_industries": r.applicable_industries,
            "min_employee_threshold": r.min_employee_threshold, 
            "last_updated": r.last_updated,
            "rules": [{"id": rule.id} for rule in r.rules], # For .length in frontend
            "severity": max_severity,
            "diffs": service.get_diffs(r.id)
        })
    return result


@router.get("/{regulation_id}")
async def get_regulation(regulation_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = RegulationService(db)
    reg = service.get_by_id(regulation_id)
    
    # Calculate max severity
    severities = [rule.severity for rule in reg.rules]
    max_severity = "medium"
    if "critical" in severities: max_severity = "critical"
    elif "high" in severities: max_severity = "high"
    
    return {
        "id": reg.id, 
        "act_name": reg.act_name, 
        "act_code": reg.act_code,
        "category": reg.category, 
        "description": reg.description,
        "applicable_states": reg.applicable_states, 
        "severity": max_severity,
        "rules": [{"id": r.id} for r in reg.rules],
        "rulesList": [
            {
                "id": r.id, 
                "section": r.section_number, 
                "title": r.rule_title,
                "rule_description": r.rule_description, 
                "requirement": r.requirement,
                "applicable_state": r.applicable_state, 
                "penalty": f"₹{r.penalty_amount:,.0f}" if r.penalty_amount else "N/A",
                "severity": r.severity, 
                "effective_date": r.effective_date,
                "change_summary": r.change_summary
            } for r in reg.rules
        ],
        "diffs": [
            {
                "id": d.rule_id,
                "section": "Rule Change",
                "change": f"Updated {d.field}: {d.old_value} -> {d.new_value}",
                "date": d.change_date.strftime("%Y-%m-%d") if d.change_date else "N/A",
                "type": "update"
            } for d in service.get_diffs(reg.id)
        ]
    }


@router.get("/{regulation_id}/rules")
async def get_rules(regulation_id: int, state: Optional[str] = None,
                    db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = RegulationService(db)
    return service.get_rules(regulation_id, state)


@router.get("/{regulation_id}/diffs")
async def get_diffs(regulation_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = RegulationService(db)
    return service.get_diffs(regulation_id)
