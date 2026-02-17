"""Policy Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PolicyUpload(BaseModel):
    policy_type: str  # wage_policy, shift_policy, overtime_policy, attendance, handbook, leave_policy
    state: str = "all"
    department: Optional[str] = None
    tags: List[str] = []


class PolicyResponse(BaseModel):
    id: str
    company_id: int
    filename: str
    original_filename: str
    policy_type: str
    state: str
    version: int
    status: str
    file_size: int
    file_type: str
    chunk_count: int
    embedding_status: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class PolicyListResponse(BaseModel):
    policies: List[PolicyResponse]
    total: int
    page: int
    page_size: int
