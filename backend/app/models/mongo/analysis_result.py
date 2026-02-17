"""Analysis Result - MongoDB Model"""
from datetime import datetime


class AnalysisResult:
    """Schema for AI analysis results stored in MongoDB"""
    
    COLLECTION = "analysis_results"
    
    @staticmethod
    def create(
        company_id: int,
        regulation_rule_id: int,
        policy_document_id: str,
        **kwargs
    ) -> dict:
        return {
            "company_id": company_id,
            "regulation_rule_id": regulation_rule_id,
            "policy_document_id": policy_document_id,
            
            # Analysis
            "comparison_result": kwargs.get("comparison_result", {}),
            "compliance_status": kwargs.get("compliance_status", "pending"),
            "confidence_score": kwargs.get("confidence_score", 0.0),
            
            # Retrieved context
            "regulation_chunks": kwargs.get("regulation_chunks", []),
            "policy_chunks": kwargs.get("policy_chunks", []),
            
            # AI reasoning
            "reasoning": kwargs.get("reasoning", ""),
            "suggested_corrections": kwargs.get("suggested_corrections", []),
            
            # LangGraph state
            "graph_state": kwargs.get("graph_state", {}),
            "graph_nodes_executed": kwargs.get("graph_nodes_executed", []),
            
            # Audit
            "model_used": kwargs.get("model_used", "gpt-4-turbo-preview"),
            "prompt_tokens": kwargs.get("prompt_tokens", 0),
            "completion_tokens": kwargs.get("completion_tokens", 0),
            
            "created_at": datetime.utcnow(),
        }
