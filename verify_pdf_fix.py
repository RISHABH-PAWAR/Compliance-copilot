import sys
import os
sys.path.append('backend')
from app.core.database import SessionLocal
from app.services.report_service import ReportService
from app.schemas.report import ReportRequest

def verify_reports():
    db = SessionLocal()
    service = ReportService(db)
    
    print("Testing Report Generation...")
    res = service.generate_report(1, 'compliance_summary')
    report_id = res['id']
    path = service.get_report_file(report_id)
    
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"SUCCESS: Report {report_id} generated at {path}")
        print(f"Size: {size} bytes")
        
        # Check first few bytes for PDF header
        with open(path, 'rb') as f:
            header = f.read(5)
            print(f"PDF Header: {header}")
            if header == b'%PDF-':
                print("VALID PDF HEADER FOUND")
            else:
                print("INVALID PDF HEADER")
    else:
        print(f"FAILED: Report not found at {path}")

    print("\nTesting Historical Report Reconstruction...")
    mock_id = "rep_999_test"
    mock_path = service.get_report_file(mock_id)
    if os.path.exists(mock_path):
        print(f"SUCCESS: Mock report {mock_id} reconstructed at {mock_path}")
        with open(mock_path, 'rb') as f:
            header = f.read(5)
            if header == b'%PDF-':
                print("VALID PDF HEADER FOUND FOR MOCK")
    else:
        print(f"FAILED: Mock report not reconstructed")

if __name__ == "__main__":
    verify_reports()
