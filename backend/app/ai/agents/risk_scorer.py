"""Risk Scorer Agent - LangGraph Node 5-6"""
from typing import TypedDict
from app.core.logging import get_logger

logger = get_logger("risk_scorer")


class RiskState(TypedDict):
    penalty_amount: float
    inspection_frequency: str
    employee_count: int
    employee_threshold: int
    urgency_factor: float
    risk_score: float
    risk_level: str
    requires_human_review: bool
    status: str


def calculate_risk(state: RiskState) -> RiskState:
    """Node 5: Calculate deterministic risk score"""
    FREQ_SCORES = {"monthly": 3.0, "quarterly": 2.5, "semi_annually": 2.0, "annually": 1.5, "on_complaint": 1.0}
    
    penalty_weight = min(state.get("penalty_amount", 0) / 100000, 5.0)
    inspection_score = FREQ_SCORES.get(state.get("inspection_frequency", "annually"), 1.0)
    impact = min(state.get("employee_count", 100) / max(state.get("employee_threshold", 1), 1), 3.0)
    urgency = state.get("urgency_factor", 1.0)
    
    total = (penalty_weight * 2) + (inspection_score * 1.5) + impact + urgency
    normalized = min((total / 20) * 100, 100)
    
    if normalized >= 75: level = "critical"
    elif normalized >= 50: level = "high"
    elif normalized >= 25: level = "medium"
    else: level = "low"
    
    state["risk_score"] = round(normalized, 1)
    state["risk_level"] = level
    state["status"] = "scored"
    
    logger.info("risk_calculated", score=normalized, level=level)
    return state


def check_human_review(state: RiskState) -> RiskState:
    """Node 6: If HIGH/CRITICAL risk, trigger human review"""
    if state.get("risk_level") in ("critical", "high"):
        state["requires_human_review"] = True
        state["status"] = "human_review_required"
        logger.info("human_review_triggered", risk_level=state["risk_level"])
    else:
        state["requires_human_review"] = False
        state["status"] = "auto_approved"
    return state
