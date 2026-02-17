"""Policy Analyzer Agent - LangGraph Node 3"""
from typing import TypedDict, List
from app.core.logging import get_logger

logger = get_logger("policy_analyzer")


class PolicyAnalysisState(TypedDict):
    company_id: int
    regulation_rule_id: int
    rule_text: str
    policy_chunks: list
    status: str


def retrieve_company_policies(state: PolicyAnalysisState) -> PolicyAnalysisState:
    """Node 3: Retrieve related company policies from vector store"""
    try:
        from app.ai.retrieval import HybridRetrieval
        
        retrieval = HybridRetrieval()
        namespace = f"company_{state['company_id']}"
        
        # Search for related policy chunks
        results = retrieval.vectorstore.search(
            query=state["rule_text"],
            namespace=namespace,
            top_k=5,
        )
        
        state["policy_chunks"] = results
        state["status"] = "policies_retrieved"
        logger.info("policies_retrieved", company_id=state["company_id"], count=len(results))
    except Exception as e:
        logger.error("policy_retrieval_failed", error=str(e))
        state["policy_chunks"] = []
        state["status"] = "retrieval_failed"
    
    return state
