import pytest

from app.agents.exceptions import LLMAnalysisError
from app.agents.graph import run_lead_analysis
from app.core.enums import Intent, Qualification, RecommendedAction
from app.schemas.analysis import GeneratedResponse, LeadAnalysisResult

COMPANY_CONTEXT = {
    "name": "Acme Sales",
    "product_description": "Plataforma de automação comercial",
    "products": [{"name": "Acme CRM", "description": "Gestao de funil comercial"}],
    "ideal_customer_profile": "Empresas B2B com 20-500 funcionários",
    "pain_points": ["perda de leads", "follow-up manual"],
    "communication_tone": "professional",
}

VALID_ANALYSIS = LeadAnalysisResult(
    qualification=Qualification.QUALIFIED,
    score=87,
    confidence=0.91,
    intent=Intent.HIGH,
    pain_points=["perda de leads"],
    reasons=["Empresa dentro do ICP", "Problema compatível com o produto"],
    recommended_action=RecommendedAction.SCHEDULE_DEMO,
)

VALID_GENERATED = GeneratedResponse(
    response="Olá! Obrigado pelo contato, vamos agendar uma demonstração.",
    call_script="Abrir agradecendo o contato e confirmar o nome da empresa.",
)


class _FakeStructuredLLM:
    def __init__(self, result=None, exc=None, capture=None):
        self._result = result
        self._exc = exc
        self._capture = capture

    def invoke(self, messages):
        if self._capture is not None:
            self._capture.append(messages)
        if self._exc is not None:
            raise self._exc
        return self._result


class _FakeLLM:
    """Simula um chat model: cada schema pedido via `with_structured_output` recebe seu
    próprio resultado/exceção mockados — analyze_lead pede `LeadAnalysisResult`,
    generate_response pede `GeneratedResponse`. As mensagens enviadas pra `GeneratedResponse`
    ficam gravadas em `response_messages`, pra inspecionar o prompt de fato construído."""

    def __init__(self, analysis_result=None, analysis_exc=None, response_result=None, response_exc=None):
        self._analysis_result = analysis_result
        self._analysis_exc = analysis_exc
        self._response_result = response_result
        self._response_exc = response_exc
        self.response_messages: list = []

    def with_structured_output(self, schema):
        if schema is LeadAnalysisResult:
            return _FakeStructuredLLM(result=self._analysis_result, exc=self._analysis_exc)
        if schema is GeneratedResponse:
            return _FakeStructuredLLM(
                result=self._response_result, exc=self._response_exc, capture=self.response_messages
            )
        raise AssertionError(f"schema inesperado: {schema}")


def _patch_llm(monkeypatch, **kwargs):
    fake = _FakeLLM(**kwargs)
    monkeypatch.setattr("app.agents.nodes.get_llm", lambda: fake)
    return fake


def test_run_lead_analysis_returns_valid_structured_result_and_call_script(monkeypatch):
    _patch_llm(monkeypatch, analysis_result=VALID_ANALYSIS, response_result=VALID_GENERATED)

    analysis, response, call_script = run_lead_analysis(
        "Preciso de ajuda com meus leads", COMPANY_CONTEXT, channel="manual"
    )

    assert isinstance(analysis, LeadAnalysisResult)
    assert 0 <= analysis.score <= 100
    assert analysis.qualification == Qualification.QUALIFIED
    assert response == VALID_GENERATED.response
    assert call_script == VALID_GENERATED.call_script


@pytest.mark.parametrize("channel", ["manual", "telegram", "landing_page"])
def test_run_lead_analysis_works_for_every_channel(monkeypatch, channel):
    _patch_llm(monkeypatch, analysis_result=VALID_ANALYSIS, response_result=VALID_GENERATED)

    analysis, response, call_script = run_lead_analysis("mensagem", COMPANY_CONTEXT, channel=channel)

    assert response and call_script


def test_run_lead_analysis_raises_llm_analysis_error_on_invalid_analysis_output(monkeypatch):
    _patch_llm(monkeypatch, analysis_result={"score": 999}, response_result=VALID_GENERATED)

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT, channel="manual")


def test_run_lead_analysis_raises_llm_analysis_error_on_analysis_call_failure(monkeypatch):
    _patch_llm(monkeypatch, analysis_exc=TimeoutError("timeout"), response_result=VALID_GENERATED)

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT, channel="manual")


def test_run_lead_analysis_raises_llm_analysis_error_when_response_generation_fails(monkeypatch):
    _patch_llm(monkeypatch, analysis_result=VALID_ANALYSIS, response_exc=ConnectionError("indisponível"))

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT, channel="manual")


@pytest.mark.parametrize(
    ("channel", "expected_snippet"),
    [
        ("telegram", "mensagem curta e direta de chat"),
        ("manual", "formato de email"),
        ("landing_page", "formato de email"),
    ],
)
def test_generate_response_prompt_includes_channel_instruction(monkeypatch, channel, expected_snippet):
    """A formatação por canal (SPEC.md secao 7) é uma instrução de prompt — verifica que o
    texto certo chega no prompt para cada canal, sem depender do texto exato que o LLM devolve."""
    fake = _patch_llm(monkeypatch, analysis_result=VALID_ANALYSIS, response_result=VALID_GENERATED)

    run_lead_analysis("mensagem", COMPANY_CONTEXT, channel=channel)

    assert len(fake.response_messages) == 1
    system_message = fake.response_messages[0][0]
    assert expected_snippet in system_message.content


def test_run_lead_analysis_raises_llm_analysis_error_on_invalid_response_output(monkeypatch):
    _patch_llm(
        monkeypatch,
        analysis_result=VALID_ANALYSIS,
        response_result={"response": "", "call_script": "x"},
    )

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT, channel="manual")
