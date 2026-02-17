"""Alert Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AlertResponse(BaseModel):
    id: int
    company_id: int
    title: str
    description: str
    alert_type: str
    priority: str
    regulation_id: Optional[int] = None
    is_read: bool
    is_dismissed: bool
    action_required: bool
    action_url: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    unread_count: int
