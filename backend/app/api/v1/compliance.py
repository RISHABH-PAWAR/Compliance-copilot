"""Compliance Analysis Endpoints"""
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.compliance_service import ComplianceService

router = APIRouter()


@router.get("/overview")
async def compliance_overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ComplianceService(db)
    return service.analyze_company_compliance(user.company_id or 1)


@router.get("/gaps")
async def compliance_gaps(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ComplianceService(db)
    overview = service.analyze_company_compliance(user.company_id or 1)
    return {"gaps": overview.gaps, "total": len(overview.gaps)}


@router.get("/state-map")
async def state_compliance_map(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ComplianceService(db)
    return service.get_state_compliance_map(user.company_id or 1)


@router.get("/checklist")
async def compliance_checklist(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ComplianceService(db)
    return service.generate_checklist(user.company_id or 1)


@router.get("/risk-score/{rule_id}")
async def get_risk_score(rule_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.sql.regulation import RegulationRule
    rule = db.query(RegulationRule).filter(RegulationRule.id == rule_id).first()
    if not rule:
        return {"error": "Rule not found"}
    service = ComplianceService(db)
    return service.calculate_risk_score(rule)
