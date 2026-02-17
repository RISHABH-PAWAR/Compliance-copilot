"""Company Service"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.sql.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CompanyCreate) -> Company:
        company = Company(**data.model_dump())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get(self, company_id: int) -> Company:
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    def update(self, company_id: int, data: CompanyUpdate) -> Company:
        company = self.get(company_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
        self.db.commit()
        self.db.refresh(company)
        return company

    def list_all(self, skip: int = 0, limit: int = 20):
        return self.db.query(Company).filter(Company.is_active == True).offset(skip).limit(limit).all()

    def get_operational_states(self, company_id: int):
        company = self.get(company_id)
        return company.operational_states or []
