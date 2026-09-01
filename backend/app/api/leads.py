import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.lead import LeadCreate, LeadDetail, LeadRead
from app.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)) -> LeadRead:
    return lead_service.create(db, data)


@router.get("", response_model=list[LeadDetail])
def list_leads(db: Session = Depends(get_db)) -> list[LeadDetail]:
    return lead_service.list_leads(db)


@router.get("/{lead_id}", response_model=LeadDetail)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)) -> LeadDetail:
    return lead_service.get_detail(db, lead_id)
