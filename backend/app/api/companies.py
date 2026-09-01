from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services import company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)) -> CompanyRead:
    return company_service.create(db, data)


@router.get("", response_model=CompanyRead)
def get_company(db: Session = Depends(get_db)) -> CompanyRead:
    return company_service.get(db)


@router.put("", response_model=CompanyRead)
def update_company(data: CompanyUpdate, db: Session = Depends(get_db)) -> CompanyRead:
    return company_service.update(db, data)
