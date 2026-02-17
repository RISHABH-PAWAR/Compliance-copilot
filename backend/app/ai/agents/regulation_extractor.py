"""Regulation Extractor Agent - LangGraph Node 1-2"""
from typing import TypedDict, Optional
from app.core.logging import get_logger

logger = get_logger("regulation_extractor")


class RegulationState(TypedDict):
    regulation_text: str
    extracted_rules: list
    applicable_state: str
    act_code: str
    status: str


def identify_regulation(state: RegulationState) -> RegulationState:
    """Node 1: Identify which regulation the text belongs to"""
    text = state.get("regulation_text", "")
    
    act_codes = {
        "factories": "FACTORIES_ACT",
        "minimum wage": "MIN_WAGES_ACT",
        "shop": "SHOPS_EST_ACT",
        "provident fund": "EPF_ACT",
        "epf": "EPF_ACT",
        "esi": "ESI_ACT",
        "payment of wage": "PAYMENT_WAGES_ACT",
        "bonus": "BONUS_ACT",
    }
    
    detected = "UNKNOWN"
    for keyword, code in act_codes.items():
        if keyword in text.lower():
            detected = code
            break
    
    state["act_code"] = detected
    state["status"] = "identified"
    logger.info("regulation_identified", act_code=detected)
    return state


def extract_rules(state: RegulationState) -> RegulationState:
    """Node 2: Extract structured rules from regulation text"""
    try:
        from app.ai.chains import compliance_chains
        result = compliance_chains.extract_regulation_rules(state["regulation_text"])
        state["extracted_rules"] = result.get("rules", [])
        state["status"] = "extracted"
    except Exception as e:
        logger.error("extraction_failed", error=str(e))
        state["extracted_rules"] = []
        state["status"] = "extraction_failed"
    return state
