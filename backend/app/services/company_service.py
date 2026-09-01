import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Company
from app.repositories import company_repository
from app.schemas.company import CompanyCreate


def create(db: Session, data: CompanyCreate) -> Company:
    return company_repository.create(db, data)


def get(db: Session, company_id: uuid.UUID) -> Company:
    company = company_repository.get_by_id(db, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    return company
