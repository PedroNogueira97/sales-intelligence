import pytest
from pydantic import ValidationError

from app.schemas.analysis import LeadAnalysisResult
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.lead import LeadCreate

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
