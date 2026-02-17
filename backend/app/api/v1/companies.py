"""Company Endpoints"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.post("/", response_model=CompanyResponse)
async def create_company(data: CompanyCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    return CompanyService(db).create(data)


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CompanyService(db).list_all(skip, limit)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CompanyService(db).get(company_id)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, data: CompanyUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CompanyService(db).update(company_id, data)
