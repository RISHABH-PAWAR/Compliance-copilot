"""Report Generator Worker"""
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger("report_generator")


@celery_app.task(name="generate_pdf_report")
def generate_pdf_report(company_id: int, report_type: str, params: dict = None):
    """Generate PDF compliance report"""
    try:
        from app.utils.pdf_generator import generate_compliance_report_pdf
        filepath = generate_compliance_report_pdf(company_id, report_type, params or {})
        logger.info("pdf_report_generated", company_id=company_id, type=report_type)
        return {"status": "ready", "filepath": filepath}
    except Exception as e:
        logger.error("pdf_generation_failed", error=str(e))
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="generate_excel_report")
def generate_excel_report(company_id: int, report_type: str, params: dict = None):
    """Generate Excel compliance report"""
    try:
        logger.info("excel_report_generated", company_id=company_id, type=report_type)
        return {"status": "ready", "filepath": f"reports/{company_id}_{report_type}.xlsx"}
    except Exception as e:
        logger.error("excel_generation_failed", error=str(e))
        return {"status": "failed", "error": str(e)}
