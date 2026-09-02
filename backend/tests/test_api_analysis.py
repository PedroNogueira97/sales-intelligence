import uuid

from app.agents.exceptions import LLMAnalysisError
from app.core.enums import InteractionType, LeadChannel, LeadStatus, Qualification, RecommendedAction
from app.models import Analysis, Interaction, Lead
from app.schemas.analysis import LeadAnalysisResult


def _create_company(client, **overrides):
    payload = {"name": "Acme Sales"}
    payload.update(overrides)
    return client.post("/companies", json=payload).json()


def _create_lead(client, **overrides):
    payload = {
        "name": "Joao",
        "email": "joao@example.com",
        "message": "Preciso de ajuda com meus leads, temos 50 funcionarios.",
    }
    payload.update(overrides)
    return client.post("/leads", json=payload).json()


def _mock_run_lead_analysis(
    monkeypatch,
    result: LeadAnalysisResult | None,
    response_text="Resposta sugerida.",
    call_script="Abrir agradecendo o contato.",
    exc=None,
):
    def _fake(lead_message, company_context, channel):
        if exc is not None:
            raise exc
        return result, response_text, call_script

    monkeypatch.setattr("app.services.analysis_service.run_lead_analysis", _fake)


def _result(
    score=87,
    qualification=Qualification.QUALIFIED,
    intent="high",
    confidence=0.91,
    pain_points=None,
    reasons=None,
    recommended_action=RecommendedAction.SCHEDULE_DEMO,
) -> LeadAnalysisResult:
    return LeadAnalysisResult(
        qualification=qualification,
        score=score,
        confidence=confidence,
        intent=intent,
        pain_points=pain_points or ["perda de leads"],
        reasons=reasons or ["Empresa dentro do ICP", "Problema compatível com o produto"],
        recommended_action=recommended_action,
    )


def test_analyze_qualified_lead_persists_high_score_and_schedules_demo(client, db_session, monkeypatch):
    _create_company(client)
    lead = _create_lead(client)
    _mock_run_lead_analysis(
        monkeypatch,
        _result(score=90, qualification=Qualification.QUALIFIED, confidence=0.9, recommended_action=RecommendedAction.DISCARD),
    )

    response = client.post(f"/leads/{lead['id']}/analyze")

    assert response.status_code == 200
    assert response.json() == {"lead_id": lead["id"], "status": "analyzed"}

    db_session.expire_all()
    db_lead = db_session.get(Lead, uuid.UUID(lead["id"]))
    assert db_lead.status == LeadStatus.ANALYZED

    analysis = db_session.query(Analysis).filter(Analysis.lead_id == db_lead.id).one()
    assert analysis.score == 90
    assert analysis.qualification == Qualification.QUALIFIED
    # regra determinística vence a sugestão do LLM (IA sugere, sistema decide)
    assert analysis.recommended_action == RecommendedAction.SCHEDULE_DEMO
    assert analysis.call_script

    interaction_types = {
        i.type for i in db_session.query(Interaction).filter(Interaction.lead_id == db_lead.id).all()
    }
    assert InteractionType.ANALYSIS_STARTED in interaction_types
    assert InteractionType.ANALYSIS_COMPLETED in interaction_types
    assert InteractionType.RESPONSE_GENERATED in interaction_types


def test_analyze_unqualified_lead_results_in_low_priority_and_discard(client, monkeypatch):
    _create_company(client)
    lead = _create_lead(client, message="Só olhando, sem interesse real.")
    _mock_run_lead_analysis(
        monkeypatch,
        _result(score=10, qualification=Qualification.UNQUALIFIED, intent="low", confidence=0.9, pain_points=[]),
    )

    client.post(f"/leads/{lead['id']}/analyze")
    analysis = client.get(f"/leads/{lead['id']}/analysis").json()

    assert analysis["score"] == 10
    assert analysis["qualification"] == "unqualified"
    assert analysis["recommended_action"] == "discard"


def test_analyze_ambiguous_lead_accepts_maybe_qualification(client, monkeypatch):
    _create_company(client)
    lead = _create_lead(client)
    _mock_run_lead_analysis(
        monkeypatch,
        _result(score=60, qualification=Qualification.MAYBE, intent="medium", confidence=0.7),
    )

    client.post(f"/leads/{lead['id']}/analyze")
    analysis = client.get(f"/leads/{lead['id']}/analysis").json()

    assert analysis["qualification"] == "maybe"
    assert analysis["recommended_action"] == "contact_salesperson"


def test_analyze_marks_lead_as_error_and_does_not_persist_invalid_analysis(client, db_session, monkeypatch):
    _create_company(client)
    lead = _create_lead(client)
    _mock_run_lead_analysis(monkeypatch, result=None, exc=LLMAnalysisError("LLM indisponível"))

    response = client.post(f"/leads/{lead['id']}/analyze")

    assert response.status_code == 502
    assert "stack" not in response.text.lower()
    assert "traceback" not in response.text.lower()

    db_session.expire_all()
    db_lead = db_session.get(Lead, uuid.UUID(lead["id"]))
    assert db_lead.status == LeadStatus.ERROR
    assert db_session.query(Analysis).filter(Analysis.lead_id == db_lead.id).count() == 0

    interaction_types = {
        i.type for i in db_session.query(Interaction).filter(Interaction.lead_id == db_lead.id).all()
    }
    assert InteractionType.ANALYSIS_FAILED in interaction_types


def test_analyze_passes_lead_channel_to_graph(client, db_session, monkeypatch):
    company_id = uuid.UUID(_create_company(client)["id"])
    # canal telegram é criado pelo polling em background (Fase 5), não por um endpoint REST —
    # aqui só precisamos de um lead com esse canal pra testar o repasse ao grafo.
    lead = Lead(
        company_id=company_id,
        name="Maria",
        telegram_chat_id="123456789",
        message="Oi",
        channel=LeadChannel.TELEGRAM,
    )
    db_session.add(lead)
    db_session.commit()

    received_channels = []

    def _fake(lead_message, company_context, channel):
        received_channels.append(channel)
        return _result(), "resposta", "roteiro"

    monkeypatch.setattr("app.services.analysis_service.run_lead_analysis", _fake)

    client.post(f"/leads/{lead.id}/analyze")

    assert received_channels == ["telegram"]


def test_analyze_returns_404_for_unknown_lead(client, monkeypatch):
    _mock_run_lead_analysis(monkeypatch, result=_result())

    response = client.post(f"/leads/{uuid.uuid4()}/analyze")

    assert response.status_code == 404


def test_get_analysis_returns_404_before_lead_is_analyzed(client):
    _create_company(client)
    lead = _create_lead(client)

    response = client.get(f"/leads/{lead['id']}/analysis")

    assert response.status_code == 404


def test_get_analysis_reflects_persisted_result_on_reload(client, monkeypatch):
    _create_company(client)
    lead = _create_lead(client)
    _mock_run_lead_analysis(
        monkeypatch,
        _result(),
        response_text="Olá, vamos agendar uma conversa?",
        call_script="Perguntar sobre o volume de leads perdidos hoje.",
    )

    client.post(f"/leads/{lead['id']}/analyze")

    first = client.get(f"/leads/{lead['id']}/analysis").json()
    second = client.get(f"/leads/{lead['id']}/analysis").json()

    assert first == second
    assert second["response"] == "Olá, vamos agendar uma conversa?"
    assert second["call_script"] == "Perguntar sobre o volume de leads perdidos hoje."
    assert len(second["reasons"]) >= 1
