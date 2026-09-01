import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.agents.exceptions import LLMAnalysisError
from app.agents.llm import get_llm
from app.agents.prompts import (
    ANALYZE_LEAD_SYSTEM_PROMPT,
    ANALYZE_LEAD_USER_PROMPT,
    GENERATE_RESPONSE_SYSTEM_PROMPT,
    GENERATE_RESPONSE_USER_PROMPT,
)
from app.agents.state import LeadAnalysisState
from app.schemas.analysis import LeadAnalysisResult

logger = logging.getLogger(__name__)


def analyze_lead(state: LeadAnalysisState) -> dict:
    company_context = json.dumps(state["company_context"], ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(content=ANALYZE_LEAD_SYSTEM_PROMPT.format(company_context=company_context)),
        HumanMessage(content=ANALYZE_LEAD_USER_PROMPT.format(lead_message=state["lead_message"])),
    ]

    try:
        structured_llm = get_llm().with_structured_output(LeadAnalysisResult)
        result = structured_llm.invoke(messages)
    except (ValidationError, ValueError) as exc:
        logger.warning("Saída inválida do LLM em analyze_lead: %s", exc)
        raise LLMAnalysisError("O LLM retornou uma análise em formato inválido.") from exc
    except Exception as exc:  # timeout, rate limit, indisponibilidade, etc.
        logger.warning("Falha ao chamar o LLM em analyze_lead: %s", exc)
        raise LLMAnalysisError("Não foi possível obter uma análise do LLM.") from exc

    if not isinstance(result, LeadAnalysisResult):
        raise LLMAnalysisError("O LLM retornou uma análise em formato inválido.")

    return {"analysis": result.model_dump(mode="json")}


def generate_response(state: LeadAnalysisState) -> dict:
    company_context = json.dumps(state["company_context"], ensure_ascii=False, indent=2)
    analysis = json.dumps(state["analysis"], ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(
            content=GENERATE_RESPONSE_SYSTEM_PROMPT.format(
                company_context=company_context, analysis=analysis
            )
        ),
        HumanMessage(content=GENERATE_RESPONSE_USER_PROMPT.format(lead_message=state["lead_message"])),
    ]

    try:
        ai_message = get_llm().invoke(messages)
    except Exception as exc:
        logger.warning("Falha ao chamar o LLM em generate_response: %s", exc)
        raise LLMAnalysisError("Não foi possível gerar a resposta comercial.") from exc

    content = ai_message.content
    if not isinstance(content, str) or not content.strip():
        raise LLMAnalysisError("O LLM retornou uma resposta comercial vazia ou inválida.")

    return {"response": content}
