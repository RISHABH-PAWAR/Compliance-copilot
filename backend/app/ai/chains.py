"""LangChain Chains for Compliance Analysis"""
from typing import Optional
from app.config import get_settings

settings = get_settings()


class ComplianceChains:
    """LangChain chains for compliance document analysis"""

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            from app.ai.llm import get_llm
            self._llm = get_llm(temperature=0)
        return self._llm

    def extract_regulation_rules(self, text: str) -> dict:
        """Extract structured rules from regulation text"""
        if not self.llm:
            return {"rules": [], "status": "llm_unavailable"}

        from langchain.prompts import ChatPromptTemplate
        from app.ai.prompts.extraction import REGULATION_EXTRACTION_PROMPT

        prompt = ChatPromptTemplate.from_template(REGULATION_EXTRACTION_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({"regulation_text": text})
        return {"rules": result.content, "status": "success"}

    def compare_policy_vs_rule(self, policy_text: str, rule_text: str) -> dict:
        """Compare company policy against regulation rule"""
        if not self.llm:
            return {"status": "llm_unavailable", "comparison": None}

        from langchain.prompts import ChatPromptTemplate
        from app.ai.prompts.comparison import POLICY_COMPARISON_PROMPT

        prompt = ChatPromptTemplate.from_template(POLICY_COMPARISON_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({"policy_text": policy_text, "rule_text": rule_text})
        return {"comparison": result.content, "status": "success"}

    def analyze_compliance(self, context: str) -> dict:
        """General compliance analysis"""
        if not self.llm:
            return {"status": "llm_unavailable", "analysis": None}

        from langchain.prompts import ChatPromptTemplate
        from app.ai.prompts.analysis import COMPLIANCE_ANALYSIS_PROMPT

        prompt = ChatPromptTemplate.from_template(COMPLIANCE_ANALYSIS_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({"context": context})
        return {"analysis": result.content, "status": "success"}


compliance_chains = ComplianceChains()
