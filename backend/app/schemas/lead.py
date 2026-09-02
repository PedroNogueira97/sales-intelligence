import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import LeadChannel, LeadStatus
from app.schemas.analysis import AnalysisRead


class LeadCreate(BaseModel):
    """Criação manual de lead (`POST /leads`) — canal sempre `manual` (SPEC.md secao 7)."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    company_name: str | None = None
    message: str = Field(min_length=1)


class LandingPageLeadCreate(BaseModel):
    """Simula o envio do formulário da landing page fake (`POST /leads/landing-page`)."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    message: str = Field(min_length=1)


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    email: str | None
    phone: str | None
    telegram_chat_id: str | None
    company_name: str | None
    message: str
    channel: LeadChannel
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content: str
    created_at: datetime


class AddLeadMessage(BaseModel):
    """Registro manual de mais uma interação (`POST /leads/{lead_id}/messages`, SPEC.md secao 8)
    — usado pra canais sem recebimento automático (`manual`/`landing_page`)."""

    content: str = Field(min_length=1)


class LeadDetail(LeadRead):
    """Usado por GET /leads/{lead_id} e GET /leads: lead + histórico + análise mais recente."""

    has_sufficient_context: bool
    messages: list[LeadMessageRead]
    analysis: AnalysisRead | None = None
