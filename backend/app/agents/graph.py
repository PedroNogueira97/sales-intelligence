from langgraph.graph import END, START, StateGraph

from app.agents.nodes import analyze_lead, generate_response
from app.agents.state import LeadAnalysisState
from app.schemas.analysis import LeadAnalysisResult

_builder = StateGraph(LeadAnalysisState)
_builder.add_node("analyze_lead", analyze_lead)
_builder.add_node("generate_response", generate_response)
_builder.add_edge(START, "analyze_lead")
_builder.add_edge("analyze_lead", "generate_response")
_builder.add_edge("generate_response", END)
_graph = _builder.compile()


def run_lead_analysis(
    lead_message: str, company_context: dict, channel: str
) -> tuple[LeadAnalysisResult, str, str]:
    """Ponto de entrada único do grafo para a service layer.

    Mantém `StateGraph`/`invoke` encapsulados no módulo `agents` — a service layer
    (app.services.analysis_service) não conhece LangGraph, só recebe o resultado
    estruturado já validado, o texto da resposta comercial (formatado de acordo com
    `channel`, SPEC.md secao 7) e o roteiro de ligação sugerido.
    """
    initial_state: LeadAnalysisState = {
        "lead_id": "",
        "lead_message": lead_message,
        "company_context": company_context,
        "channel": channel,
        "analysis": None,
        "response": None,
        "call_script": None,
    }
    final_state = _graph.invoke(initial_state)
    analysis = LeadAnalysisResult.model_validate(final_state["analysis"])
    response = final_state["response"]
    call_script = final_state["call_script"]
    return analysis, response, call_script
