"""PDF Report Generator"""
from app.core.logging import get_logger
logger = get_logger("pdf_generator")


def generate_compliance_report_pdf(company_id: int, report_type: str, params: dict) -> str:
    """Generate a PDF compliance report using ReportLab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        import os

        os.makedirs("reports", exist_ok=True)
        filepath = f"reports/{company_id}_{report_type}.pdf"
        
        c = canvas.Canvas(filepath, pagesize=A4)
        c.setTitle(f"Compliance Report - {report_type}")
        c.drawString(100, 750, f"AI Compliance Copilot - {report_type.replace('_', ' ').title()}")
        c.drawString(100, 730, f"Company ID: {company_id}")
        c.drawString(100, 710, f"Generated: {params.get('date', 'N/A')}")
        c.save()
        
        logger.info("pdf_generated", filepath=filepath)
        return filepath
    except Exception as e:
        logger.error("pdf_generation_error", error=str(e))
        return ""
