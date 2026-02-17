"""Dependency Injection Module"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user


def get_company_id(current_user=Depends(get_current_user)) -> int:
    """Get current user's company ID"""
    return current_user.company_id or 1
