"""Output Formatters"""

def format_inr(amount: float) -> str:
    """Format amount in Indian Rupees with commas"""
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount / 100000:.2f} L"
    return f"₹{amount:,.0f}"

def format_risk_level(level: str) -> dict:
    colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#22c55e"}
    return {"level": level, "color": colors.get(level, "#6b7280"), "label": level.upper()}
