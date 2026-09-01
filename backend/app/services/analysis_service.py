import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.exceptions import LLMAnalysisError
from app.agents.graph import run_lead_analysis
from app.core.enums import InteractionType, LeadStatus
from app.models import Analysis, Company, Interaction, Lead
from app.repositories import analysis_repository, company_repository, lead_repository
from app.schemas.analysis import AnalysisRead
from app.services import lead_service
from app.services.classification_service import decide_recommended_action

logger = logging.getLogger(__name__)


def analyze(db: Session, lead_id: uuid.UUID) -> Lead:
    """Executa a análise do lead (SPEC.md secao 4 e 21).

    IA sugere, o sistema controla: o `recommended_action` persistido é decidido
    deterministicamente (`decide_recommended_action`), não o sugerido pelo LLM.
    """
    lead = lead_service.get(db, lead_id)
    company = company_repository.get_by_id(db, lead.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    lead.status = LeadStatus.PROCESSING
    db.add(Interaction(lead_id=lead.id, type=InteractionType.ANALYSIS_STARTED, payload=None))
    db.commit()

    try:
        result, response_text, call_script = run_lead_analysis(
            lead.message, _build_company_context(company), lead.channel.value
        )
    except LLMAnalysisError as exc:
        logger.error("Falha ao analisar lead %s: %s", lead.id, exc)
        lead.status = LeadStatus.ERROR
        db.add(
            Interaction(
                lead_id=lead.id,
                type=InteractionType.ANALYSIS_FAILED,
                payload={"error": str(exc)},
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível analisar o lead no momento. Tente novamente.",
        ) from exc

    recommended_action = decide_recommended_action(result.score, result.qualification, result.confidence)
    analysis = Analysis(
        lead_id=lead.id,
        score=result.score,
        qualification=result.qualification,
        intent=result.intent,
        confidence=result.confidence,
        pain_points=result.pain_points,
        reasons=result.reasons,
        recommended_action=recommended_action,
        response=response_text,
        call_script=call_script,
    )
    analysis_repository.create(db, analysis)

    lead.status = LeadStatus.ANALYZED
    db.add(
        Interaction(
            lead_id=lead.id,
            type=InteractionType.ANALYSIS_COMPLETED,
            payload={"score": result.score, "qualification": result.qualification.value},
        )
    )
    db.add(Interaction(lead_id=lead.id, type=InteractionType.RESPONSE_GENERATED, payload=None))
    db.commit()

    return lead


def get_analysis(db: Session, lead_id: uuid.UUID) -> AnalysisRead:
    lead_service.get(db, lead_id)
    analysis = lead_repository.get_latest_analysis(db, lead_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead ainda não foi analisado")
    return AnalysisRead.model_validate(analysis)


def _build_company_context(company: Company) -> dict:
    return {
        "name": company.name,
        "description": company.description,
        "product_description": company.product_description,
        "products": company.products,
        "ideal_customer_profile": company.ideal_customer_profile,
        "average_ticket": float(company.average_ticket) if company.average_ticket is not None else None,
        "pain_points": company.pain_points,
        "communication_tone": company.communication_tone,
    }
