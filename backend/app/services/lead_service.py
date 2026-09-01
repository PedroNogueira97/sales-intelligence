import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import InteractionType, LeadChannel, LeadStatus
from app.models import Analysis, Interaction, Lead
from app.repositories import company_repository, lead_repository
from app.schemas.analysis import AnalysisRead
from app.schemas.lead import LandingPageLeadCreate, LeadCreate, LeadDetail, LeadRead, WhatsAppLeadCreate


def create(
    db: Session,
    data: LeadCreate | WhatsAppLeadCreate | LandingPageLeadCreate,
    channel: LeadChannel,
) -> Lead:
    """Cria um lead no canal informado.

    `channel` é sempre decidido pelo endpoint que chama este service (qual rota foi usada),
    nunca por um campo que o cliente da API escolhe (SPEC.md secao 7).
    """
    company = company_repository.get_singleton(db)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Configure a empresa antes de cadastrar leads.",
        )

    lead = Lead(
        status=LeadStatus.NEW, company_id=company.id, channel=channel, **data.model_dump()
    )
    lead_repository.create(db, lead)
    db.add(Interaction(lead_id=lead.id, type=InteractionType.LEAD_CREATED, payload=None))
    db.commit()
    return lead


def get(db: Session, lead_id: uuid.UUID) -> Lead:
    lead = lead_repository.get_by_id(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead não encontrado")
    return lead


def get_detail(db: Session, lead_id: uuid.UUID) -> LeadDetail:
    lead = get(db, lead_id)
    analysis = lead_repository.get_latest_analysis(db, lead_id)
    return _to_detail(lead, analysis)


def list_leads(db: Session) -> list[LeadDetail]:
    rows = lead_repository.list_with_latest_analysis(db)
    return [_to_detail(lead, analysis) for lead, analysis in rows]


def _to_detail(lead: Lead, analysis: Analysis | None) -> LeadDetail:
    lead_data = LeadRead.model_validate(lead).model_dump()
    analysis_data = AnalysisRead.model_validate(analysis) if analysis is not None else None
    return LeadDetail(**lead_data, analysis=analysis_data)
