import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.enums import LeadChannel
from app.schemas.analysis import AnalysisRead, AnalyzeResponse
from app.schemas.lead import LandingPageLeadCreate, LeadCreate, LeadDetail, LeadRead
from app.services import analysis_service, lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)) -> LeadRead:
    return lead_service.create(db, data, channel=LeadChannel.MANUAL)


@router.post("/landing-page", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead_from_landing_page(
    data: LandingPageLeadCreate, db: Session = Depends(get_db)
) -> LeadRead:
    """Simula o envio do formulário da landing page fake (SPEC.md secao 22)."""
    return lead_service.create(db, data, channel=LeadChannel.LANDING_PAGE)


@router.get("", response_model=list[LeadDetail])
def list_leads(db: Session = Depends(get_db)) -> list[LeadDetail]:
    return lead_service.list_leads(db)


@router.get("/{lead_id}", response_model=LeadDetail)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)) -> LeadDetail:
    return lead_service.get_detail(db, lead_id)


@router.post("/{lead_id}/analyze", response_model=AnalyzeResponse)
def analyze_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)) -> AnalyzeResponse:
    lead = analysis_service.analyze(db, lead_id)
    return AnalyzeResponse(lead_id=lead.id, status=lead.status.value)


@router.get("/{lead_id}/analysis", response_model=AnalysisRead)
def get_lead_analysis(lead_id: uuid.UUID, db: Session = Depends(get_db)) -> AnalysisRead:
    return analysis_service.get_analysis(db, lead_id)
