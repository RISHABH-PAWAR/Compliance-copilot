"""Compliance Analyzer Worker"""
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger("compliance_analyzer")


@celery_app.task(name="analyze_compliance", bind=True, max_retries=3)
def analyze_compliance(self, company_id: int, regulation_id: int = None):
    """Batch compliance analysis for a company"""
    try:
        logger.info("compliance_analysis_started", company_id=company_id)
        return {"status": "completed", "company_id": company_id}
    except Exception as e:
        logger.error("compliance_analysis_failed", error=str(e))
        self.retry(countdown=120)


@celery_app.task(name="analyze_new_regulation")
def analyze_new_regulation(regulation_rule_id: int):
    """Analyze impact of new regulation on all companies"""
    logger.info("new_regulation_analysis", rule_id=regulation_rule_id)
    return {"status": "completed", "rule_id": regulation_rule_id}
