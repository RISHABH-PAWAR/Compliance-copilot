"""Compliance Checker Agent - LangGraph Node 4"""
from typing import TypedDict
from app.core.logging import get_logger

logger = get_logger("compliance_checker")


class ComplianceCheckState(TypedDict):
    rule_text: str
    policy_text: str
    compliance_status: str  # compliant, partial, violation
    gap_description: str
    suggested_correction: str
    legal_reference: str
    financial_risk: float
    inspection_risk: str
    status: str


def compare_rule_vs_policy(state: ComplianceCheckState) -> ComplianceCheckState:
    """Node 4: Compare regulation rule against company policy"""
    try:
        from app.ai.chains import compliance_chains
        
        result = compliance_chains.compare_policy_vs_rule(
            policy_text=state["policy_text"],
            rule_text=state["rule_text"],
        )
        
        if result["status"] == "success":
            state["compliance_status"] = "partial"  # AI would determine this
            state["gap_description"] = result.get("comparison", "")
            state["status"] = "compared"
        else:
            # Fallback deterministic check
            state["compliance_status"] = "partial"
            state["gap_description"] = "AI unavailable - manual review recommended"
            state["status"] = "compared_fallback"
            
        logger.info("compliance_check", status=state["compliance_status"])
    except Exception as e:
        logger.error("compliance_check_failed", error=str(e))
        state["status"] = "check_failed"
    
    return state
