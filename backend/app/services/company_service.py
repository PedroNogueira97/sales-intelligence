from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Company
from app.repositories import company_repository
from app.schemas.company import CompanyCreate, CompanyUpdate


def create(db: Session, data: CompanyCreate) -> Company:
    if company_repository.get_singleton(db) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Empresa já configurada. Este MVP suporta apenas uma empresa por instalação.",
        )
    return company_repository.create(db, data)


def get(db: Session) -> Company:
    company = company_repository.get_singleton(db)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa ainda não configurada")
    return company


def update(db: Session, data: CompanyUpdate) -> Company:
    company = get(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company
