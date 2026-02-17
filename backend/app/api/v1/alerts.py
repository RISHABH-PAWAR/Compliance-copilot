"""Alert Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("")
async def list_alerts(unread_only: bool = False, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = AlertService(db)
    return service.get_alerts(user.company_id or 1, unread_only)


@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = AlertService(db)
    return service.mark_read(alert_id, user.company_id or 1)


@router.put("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = AlertService(db)
    return service.dismiss(alert_id, user.company_id or 1)
