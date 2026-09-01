from typing import TypedDict


class LeadAnalysisState(TypedDict):
    """Estado do grafo de análise (SPEC.md secao 14)."""

    lead_id: str
    lead_message: str
    company_context: dict
    channel: str  # "manual" | "whatsapp" | "landing_page" (SPEC.md secao 7)

    analysis: dict | None
    response: str | None
    call_script: str | None
