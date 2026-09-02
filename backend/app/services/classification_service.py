from typing import Literal

from app.core.enums import Qualification, RecommendedAction

Priority = Literal["alta", "media", "baixa"]


def classify_priority(score: int) -> Priority:
    """Prioridade determinística a partir do score (SPEC.md seção 8).

    80-100 = alta prioridade
    50-79  = média prioridade
    0-49   = baixa prioridade
    """
    if score >= 80:
        return "alta"
    if score >= 50:
        return "media"
    return "baixa"


def decide_recommended_action(
    score: int, qualification: Qualification, confidence: float
) -> RecommendedAction:
    """Decisão final e determinística da próxima ação.

    O LLM sugere um `recommended_action` em `LeadAnalysisResult`, mas essa
    sugestão não é persistida diretamente — a ação final que orienta o
    vendedor segue esta regra determinística (CLAUDE.md: "IA sugere, o
    sistema controla").

    Confiança baixa (< 0.60, SPEC.md seção 11) tem prioridade sobre o
    score: se a análise não é confiável, a próxima ação é sempre pedir
    mais informação, independente da prioridade calculada.
    """
    if confidence < 0.60:
        return RecommendedAction.ASK_MORE_INFORMATION
    if score >= 80:
        return RecommendedAction.SCHEDULE_DEMO
    if score >= 50:
        return RecommendedAction.CONTACT_SALESPERSON
    if qualification == Qualification.UNQUALIFIED:
        return RecommendedAction.DISCARD
    return RecommendedAction.NURTURING


MIN_CONTEXT_CHARACTERS = 40
MIN_MESSAGE_COUNT = 3


def has_sufficient_context(messages: list[str]) -> bool:
    """Decide, sem envolver o LLM, se o histórico de um lead já tem contexto suficiente pra
    valer a pena analisar (SPEC.md seção 9).

    Uma mensagem isolada tipo "oi, tenho interesse" não deveria gerar uma análise — o sistema
    decide isso, não o LLM (CLAUDE.md princípio 1).
    """
    total_characters = sum(len(message.strip()) for message in messages)
    return total_characters >= MIN_CONTEXT_CHARACTERS or len(messages) >= MIN_MESSAGE_COUNT
