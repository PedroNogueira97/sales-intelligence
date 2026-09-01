import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import LeadStatus
from app.schemas.analysis import AnalysisRead


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    company_name: str | None = None
    message: str = Field(min_length=1)


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    email: str
    company_name: str | None
    message: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadDetail(LeadRead):
    """Usado por GET /leads/{lead_id}: lead + análise mais recente, se existir."""

    analysis: AnalysisRead | None = None
