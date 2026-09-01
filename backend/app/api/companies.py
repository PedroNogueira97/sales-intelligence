import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.company import CompanyCreate, CompanyRead
from app.services import company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)) -> CompanyRead:
    return company_service.create(db, data)


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: uuid.UUID, db: Session = Depends(get_db)) -> CompanyRead:
    return company_service.get(db, company_id)
