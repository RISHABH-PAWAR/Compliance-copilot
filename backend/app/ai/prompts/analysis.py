"""Compliance Analysis Prompt Templates"""

COMPLIANCE_ANALYSIS_PROMPT = """You are an AI compliance analyst specializing in Indian labor law for manufacturing and service companies.

Analyze the following compliance context and provide:

1. Overall Compliance Assessment
2. Critical Gaps (with legal references)
3. Risk Priority Matrix
4. Recommended Actions (ordered by urgency)
5. Documentation Checklist
6. Estimated Timeline for Remediation

Context:
{context}

Provide actionable, specific recommendations. Reference exact sections of applicable acts.
Include estimated penalty amounts in INR where applicable.
"""
