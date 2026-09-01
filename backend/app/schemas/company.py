import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    """Produto/serviço da empresa — contexto adicional para a análise (SPEC.md secao 5)."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    product_description: str | None = None
    products: list[Product] = Field(default_factory=list)
    ideal_customer_profile: str | None = None
    average_ticket: float | None = Field(default=None, ge=0)
    pain_points: list[str] = Field(default_factory=list)
    communication_tone: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    product_description: str | None = None
    products: list[Product] | None = None
    ideal_customer_profile: str | None = None
    average_ticket: float | None = Field(default=None, ge=0)
    pain_points: list[str] | None = None
    communication_tone: str | None = None


class CompanyRead(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
