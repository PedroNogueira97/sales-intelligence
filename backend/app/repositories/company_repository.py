import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Company
from app.schemas.company import CompanyCreate


def create(db: Session, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_by_id(db: Session, company_id: uuid.UUID) -> Company | None:
    return db.get(Company, company_id)


def get_singleton(db: Session) -> Company | None:
    """Este MVP suporta uma única empresa por instalação (ver CLAUDE.md: sem multi-tenancy)."""
    return db.execute(select(Company).limit(1)).scalars().first()
