"""Regulation Extraction Prompt Templates"""

REGULATION_EXTRACTION_PROMPT = """You are an Indian labor law expert. Extract structured compliance rules from the following regulation text.

For each rule found, extract:
1. Section number
2. Rule title
3. Rule description
4. Specific requirement (what the company must do)
5. Applicable state (or "all" if national)
6. Penalty amount (in INR)
7. Inspection frequency
8. Required documentation
9. Employee threshold
10. Severity (low/medium/high/critical)

Regulation Text:
{regulation_text}

Output the extracted rules as a JSON array. Be precise with legal references.
"""
