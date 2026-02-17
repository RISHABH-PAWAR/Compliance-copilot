"""Company Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    industry_type: str
    employee_count: int = 0
    operational_states: List[str] = []
    headquarters_state: Optional[str] = None


class CompanyCreate(CompanyBase):
    registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    employee_count: Optional[int] = None
    operational_states: Optional[List[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    notification_preferences: Optional[dict] = None


class CompanyResponse(CompanyBase):
    id: int
    registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    subscription_plan: str
    subscription_status: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
