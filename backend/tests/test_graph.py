from types import SimpleNamespace

import pytest

from app.agents.exceptions import LLMAnalysisError
from app.agents.graph import run_lead_analysis
from app.core.enums import Intent, Qualification, RecommendedAction
from app.schemas.analysis import LeadAnalysisResult

COMPANY_CONTEXT = {
    "name": "Acme Sales",
    "product_description": "Plataforma de automação comercial",
    "ideal_customer_profile": "Empresas B2B com 20-500 funcionários",
    "pain_points": ["perda de leads", "follow-up manual"],
    "communication_tone": "professional",
}

VALID_RESULT = LeadAnalysisResult(
    qualification=Qualification.QUALIFIED,
    score=87,
    confidence=0.91,
    intent=Intent.HIGH,
    pain_points=["perda de leads"],
    reasons=["Empresa dentro do ICP", "Problema compatível com o produto"],
    recommended_action=RecommendedAction.SCHEDULE_DEMO,
)


class _FakeStructuredLLM:
    def __init__(self, result=None, exc=None):
        self._result = result
        self._exc = exc

    def invoke(self, messages):
        if self._exc is not None:
            raise self._exc
        return self._result


class _FakeLLM:
    def __init__(self, structured_result=None, structured_exc=None, plain_content=None, plain_exc=None):
        self._structured_result = structured_result
        self._structured_exc = structured_exc
        self._plain_content = plain_content
        self._plain_exc = plain_exc

    def with_structured_output(self, schema):
        return _FakeStructuredLLM(result=self._structured_result, exc=self._structured_exc)

    def invoke(self, messages):
        if self._plain_exc is not None:
            raise self._plain_exc
        return SimpleNamespace(content=self._plain_content)


def _patch_llm(monkeypatch, **kwargs):
    fake = _FakeLLM(**kwargs)
    monkeypatch.setattr("app.agents.nodes.get_llm", lambda: fake)


def test_run_lead_analysis_returns_valid_structured_result(monkeypatch):
    _patch_llm(
        monkeypatch,
        structured_result=VALID_RESULT,
        plain_content="Olá! Obrigado pelo contato, vamos agendar uma demonstração.",
    )

    analysis, response = run_lead_analysis("Preciso de ajuda com meus leads", COMPANY_CONTEXT)

    assert isinstance(analysis, LeadAnalysisResult)
    assert 0 <= analysis.score <= 100
    assert analysis.qualification == Qualification.QUALIFIED
    assert response == "Olá! Obrigado pelo contato, vamos agendar uma demonstração."


def test_run_lead_analysis_raises_llm_analysis_error_on_invalid_structured_output(monkeypatch):
    _patch_llm(monkeypatch, structured_result={"score": 999}, plain_content="ignorado")

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT)


def test_run_lead_analysis_raises_llm_analysis_error_on_structured_call_failure(monkeypatch):
    _patch_llm(monkeypatch, structured_exc=TimeoutError("timeout"), plain_content="ignorado")

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT)


def test_run_lead_analysis_raises_llm_analysis_error_when_response_generation_fails(monkeypatch):
    _patch_llm(
        monkeypatch,
        structured_result=VALID_RESULT,
        plain_exc=ConnectionError("indisponível"),
    )

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT)


def test_run_lead_analysis_raises_llm_analysis_error_on_empty_response(monkeypatch):
    _patch_llm(monkeypatch, structured_result=VALID_RESULT, plain_content="   ")

    with pytest.raises(LLMAnalysisError):
        run_lead_analysis("mensagem", COMPANY_CONTEXT)
