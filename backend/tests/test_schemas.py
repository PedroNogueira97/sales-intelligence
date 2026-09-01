import pytest
from pydantic import ValidationError

from app.schemas.analysis import GeneratedResponse, LeadAnalysisResult
from app.schemas.company import CompanyCreate, CompanyUpdate, Product
from app.schemas.lead import LandingPageLeadCreate, LeadCreate, WhatsAppLeadCreate

VALID_ANALYSIS = dict(
    qualification="qualified",
    score=87,
    confidence=0.91,
    intent="high",
    pain_points=["perda de leads", "processo manual"],
    reasons=["Empresa dentro do ICP", "Problema compativel"],
    recommended_action="schedule_demo",
)


def test_lead_analysis_result_accepts_valid_payload():
    result = LeadAnalysisResult(**VALID_ANALYSIS)

    assert result.score == 87
    assert result.qualification == "qualified"


@pytest.mark.parametrize("score", [-1, 101, 1000])
def test_lead_analysis_result_rejects_score_out_of_range(score):
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "score": score})


@pytest.mark.parametrize("confidence", [-0.01, 1.01, 5])
def test_lead_analysis_result_rejects_confidence_out_of_range(confidence):
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "confidence": confidence})


def test_lead_analysis_result_rejects_invalid_qualification():
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "qualification": "super_qualified"})


def test_lead_analysis_result_rejects_invalid_recommended_action():
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "recommended_action": "send_whatsapp"})


def test_lead_analysis_result_rejects_more_than_five_pain_points():
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "pain_points": [f"dor {i}" for i in range(6)]})


def test_lead_analysis_result_rejects_empty_reasons():
    with pytest.raises(ValidationError):
        LeadAnalysisResult(**{**VALID_ANALYSIS, "reasons": []})


def test_company_create_accepts_minimal_payload():
    company = CompanyCreate(name="Acme Sales")

    assert company.pain_points == []
    assert company.average_ticket is None
    assert company.products == []


def test_company_create_accepts_products():
    company = CompanyCreate(
        name="Acme Sales",
        products=[
            {"name": "Acme CRM", "description": "Gestao de funil comercial"},
            {"name": "Acme Onboarding"},
        ],
    )

    assert len(company.products) == 2
    assert company.products[0] == Product(name="Acme CRM", description="Gestao de funil comercial")
    assert company.products[1].description is None


def test_product_rejects_empty_name():
    with pytest.raises(ValidationError):
        Product(name="")


def test_company_create_rejects_negative_average_ticket():
    with pytest.raises(ValidationError):
        CompanyCreate(name="Acme Sales", average_ticket=-10)


def test_company_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        CompanyCreate(name="")


def test_lead_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        LeadCreate(
            name="Joao",
            email="not-an-email",
            message="mensagem",
        )


def test_lead_create_rejects_empty_message():
    with pytest.raises(ValidationError):
        LeadCreate(
            name="Joao",
            email="joao@example.com",
            message="",
        )


def test_company_update_accepts_partial_payload():
    update = CompanyUpdate(communication_tone="casual")

    assert update.communication_tone == "casual"
    assert update.name is None
    assert update.pain_points is None
    assert update.products is None


def test_whatsapp_lead_create_accepts_minimal_payload_without_email():
    lead = WhatsAppLeadCreate(name="Joao", phone="+5511999999999", message="Oi, quero saber mais")

    assert lead.phone == "+5511999999999"
    assert not hasattr(lead, "email")


def test_whatsapp_lead_create_rejects_empty_phone():
    with pytest.raises(ValidationError):
        WhatsAppLeadCreate(name="Joao", phone="", message="mensagem")


def test_landing_page_lead_create_requires_email():
    with pytest.raises(ValidationError):
        LandingPageLeadCreate(name="Joao", email="not-an-email", message="mensagem")


def test_landing_page_lead_create_accepts_payload_without_phone():
    lead = LandingPageLeadCreate(name="Joao", email="joao@example.com", message="mensagem")

    assert lead.phone is None


def test_generated_response_accepts_valid_payload():
    generated = GeneratedResponse(response="Oi, tudo bem?", call_script="Abrir agradecendo o contato.")

    assert generated.response
    assert generated.call_script


def test_generated_response_rejects_empty_call_script():
    with pytest.raises(ValidationError):
        GeneratedResponse(response="Oi, tudo bem?", call_script="")
