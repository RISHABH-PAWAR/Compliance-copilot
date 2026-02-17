"""Policy Endpoints"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.policy_service import PolicyService

router = APIRouter()


@router.post("/upload")
async def upload_policy(
    file: UploadFile = File(...),
    policy_type: str = Form(...),
    state: str = Form("all"),
    department: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    content = await file.read()
    service = PolicyService(db)
    result = service.upload_policy(
        company_id=user.company_id or 1,
        filename=file.filename,
        policy_type=policy_type,
        raw_text=content.decode("utf-8", errors="ignore")[:5000],
        state=state,
        file_size=len(content),
        file_type=file.filename.split(".")[-1] if "." in file.filename else "unknown",
        uploaded_by=user.id,
    )
    return {"message": "Policy uploaded successfully", "policy": result}


@router.get("")
async def list_policies(
    page: int = 1, page_size: int = 20,
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    service = PolicyService(db)
    return service.get_policies(user.company_id or 1, page, page_size)


@router.get("/{policy_id}")
async def get_policy(policy_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = PolicyService(db)
    policy = service.get_policy(user.company_id or 1, policy_id)
    if not policy:
        return {"error": "Policy not found"}
    return policy


@router.patch("/{policy_id}")
async def update_policy(
    policy_id: str,
    updates: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    service = PolicyService(db)
    success = service.update_policy(user.company_id or 1, policy_id, updates)
    if not success:
        return {"error": "Failed to update policy or policy not found"}
    return {"message": "Policy updated successfully"}


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    service = PolicyService(db)
    success = service.delete_policy(user.company_id or 1, policy_id)
    if not success:
        return {"error": "Failed to delete policy or policy not found"}
    return {"message": "Policy deleted successfully"}
