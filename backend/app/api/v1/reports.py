"""Report Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.report_service import ReportService
from app.schemas.report import ReportRequest

router = APIRouter()


@router.get("")
async def list_reports(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ReportService(db)
    return service.get_recent_reports(user.company_id or 1)


@router.post("/generate")
async def generate_report(data: ReportRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ReportService(db)
    return service.generate_report(user.company_id or 1, data.report_type, data.format, data.state_filter)


@router.get("/download/{report_id}")
async def download_report(report_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ReportService(db)
    file_path = service.get_report_file(report_id)
    
    import os
    from fastapi.responses import FileResponse, HTTPException
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found. Please regenerate.")
        
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"Report_{report_id}.pdf"
    )


@router.get("/types")
async def report_types():
    return {
        "types": [
            {"id": "compliance_summary", "name": "Compliance Summary Report", "description": "Overview of all compliance gaps and status"},
            {"id": "risk_assessment", "name": "Risk Assessment Report", "description": "Detailed risk scores and exposure analysis"},
            {"id": "audit_pack", "name": "Audit Pack", "description": "Complete audit documentation package"},
            {"id": "financial_exposure", "name": "Financial Exposure Report", "description": "Penalty and cost impact analysis for CFO"},
        ]
    }
