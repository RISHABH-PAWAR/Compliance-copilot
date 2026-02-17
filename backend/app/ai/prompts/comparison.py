"""Policy Comparison Prompt Templates"""

POLICY_COMPARISON_PROMPT = """You are an Indian labor law compliance expert. Compare the company policy against the regulation rule below.

Company Policy:
{policy_text}

Regulation Rule:
{rule_text}

Analyze and determine:
1. Compliance Status: "Direct Violation", "Partial Compliance", or "Fully Compliant"
2. Gap Description: What specifically is non-compliant
3. Legal Reference: Exact section and subsection that applies
4. Financial Risk: Estimated penalty exposure in INR
5. Inspection Risk: Would this fail an inspection? (Yes/No with explanation)
6. Suggested Correction: Specific steps to achieve compliance
7. Documentation Needed: What documents need to be updated/created

Be precise, factual, and cite specific legal provisions. Do NOT provide general advice.
"""
