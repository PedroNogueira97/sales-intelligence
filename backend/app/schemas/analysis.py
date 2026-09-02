import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import Intent, Qualification, RecommendedAction


class LeadAnalysisResult(BaseModel):
    """Saída estruturada esperada do LLM no node `analyze_lead`.

    Validada antes de qualquer persistência ou uso pelo backend — ver
    skill `langgraph`: "IA interpreta. Código decide.".
    """

    qualification: Qualification
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    intent: Intent
    pain_points: list[str] = Field(default_factory=list, max_length=5)
    reasons: list[str] = Field(min_length=1)
    recommended_action: RecommendedAction


class GeneratedResponse(BaseModel):
    """Saída estruturada esperada do LLM no node `generate_response` (SPEC.md secao 13/15).

    `response` é formatado de acordo com o canal do lead (Telegram: texto curto; demais:
    formato de email) — a formatação é instrução de prompt, não branching no grafo.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    response: str = Field(min_length=1)
    call_script: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    """Corpo de resposta de POST /leads/{lead_id}/analyze (SPEC.md secao 21)."""

    lead_id: uuid.UUID
    status: str


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: uuid.UUID
    score: int
    qualification: Qualification
    intent: Intent
    confidence: float
    pain_points: list[str]
    reasons: list[str]
    recommended_action: RecommendedAction
    response: str | None
    call_script: str | None
    created_at: datetime
