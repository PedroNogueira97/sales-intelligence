from typing import TypedDict


class LeadAnalysisState(TypedDict):
    """Estado do grafo de análise (SPEC.md secao 13)."""

    lead_id: str
    lead_message: str
    company_context: dict

    analysis: dict | None
    response: str | None
