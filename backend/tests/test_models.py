import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.enums import (
    Intent,
    InteractionType,
    LeadChannel,
    LeadStatus,
    Qualification,
    RecommendedAction,
)
from app.models import Analysis, Company, Interaction, Lead


def _make_company(db_session, **overrides):
    defaults = dict(
        name="Acme Sales",
        description="Empresa de automacao comercial",
        product_description="Plataforma de gestao comercial",
        ideal_customer_profile="Empresas B2B com 20-500 funcionarios",
        average_ticket=10000,
        pain_points=["perda de leads", "follow-up manual"],
        communication_tone="professional",
    )
    defaults.update(overrides)
    company = Company(**defaults)
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


def _make_lead(db_session, company, **overrides):
    defaults = dict(
        company_id=company.id,
        name="Joao",
        email="joao@example.com",
        company_name="Prospect LTDA",
        message="Preciso de ajuda com meus leads",
    )
    defaults.update(overrides)
    lead = Lead(**defaults)
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


def test_create_company_persists_fields(db_session):
    company = _make_company(db_session)

    assert isinstance(company.id, uuid.UUID)
    assert company.pain_points == ["perda de leads", "follow-up manual"]
    assert company.created_at is not None


def test_create_lead_defaults_to_new_status(db_session):
    company = _make_company(db_session)
    lead = _make_lead(db_session, company)

    assert lead.status == LeadStatus.NEW


def test_company_products_defaults_to_empty_list(db_session):
    company = _make_company(db_session)

    assert company.products == []


def test_company_products_persist(db_session):
    products = [
        {"name": "Acme CRM", "description": "Gestao de funil comercial"},
        {"name": "Acme Onboarding", "description": None},
    ]
    company = _make_company(db_session, products=products)

    assert company.products == products


def test_lead_defaults_to_manual_channel(db_session):
    company = _make_company(db_session)
    lead = _make_lead(db_session, company)

    assert lead.channel == LeadChannel.MANUAL


def test_lead_accepts_telegram_channel_without_email(db_session):
    company = _make_company(db_session)
    lead = _make_lead(
        db_session, company, channel=LeadChannel.TELEGRAM, email=None, telegram_chat_id="123456789"
    )

    assert lead.channel == LeadChannel.TELEGRAM
    assert lead.email is None
    assert lead.telegram_chat_id == "123456789"


def test_lead_requires_existing_company(db_session):
    lead = Lead(
        company_id=uuid.uuid4(),
        name="Joao",
        email="joao@example.com",
        message="mensagem",
    )
    db_session.add(lead)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_analysis_persists_all_fields(db_session):
    company = _make_company(db_session)
    lead = _make_lead(db_session, company)

    analysis = Analysis(
        lead_id=lead.id,
        score=87,
        qualification=Qualification.QUALIFIED,
        intent=Intent.HIGH,
        confidence=0.91,
        pain_points=["perda de leads"],
        reasons=["Empresa dentro do ICP", "Problema compativel"],
        recommended_action=RecommendedAction.SCHEDULE_DEMO,
        response="Obrigado pelo contato...",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    assert 0 <= analysis.score <= 100
    assert analysis.qualification == Qualification.QUALIFIED
    assert len(analysis.reasons) == 2


def test_analysis_requires_existing_lead(db_session):
    analysis = Analysis(
        lead_id=uuid.uuid4(),
        score=50,
        qualification=Qualification.MAYBE,
        intent=Intent.UNKNOWN,
        confidence=0.5,
        pain_points=[],
        reasons=[],
        recommended_action=RecommendedAction.NURTURING,
    )
    db_session.add(analysis)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_analysis_rejects_invalid_qualification_value(db_session):
    company = _make_company(db_session)
    lead = _make_lead(db_session, company)

    with pytest.raises(Exception):
        db_session.execute(
            text(
                "INSERT INTO analyses "
                "(id, lead_id, score, qualification, intent, confidence, pain_points, reasons, recommended_action) "
                "VALUES (:id, :lead_id, :score, :qualification, :intent, :confidence, "
                "'[]'::jsonb, '[]'::jsonb, :recommended_action)"
            ),
            {
                "id": uuid.uuid4(),
                "lead_id": lead.id,
                "score": 50,
                "qualification": "not_a_real_value",
                "intent": "high",
                "confidence": 0.5,
                "recommended_action": "nurturing",
            },
        )
        db_session.commit()
    db_session.rollback()


def test_create_interaction_with_payload(db_session):
    company = _make_company(db_session)
    lead = _make_lead(db_session, company)

    interaction = Interaction(
        lead_id=lead.id, type=InteractionType.LEAD_CREATED, payload={"source": "form"}
    )
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)

    assert interaction.type == InteractionType.LEAD_CREATED
    assert interaction.payload == {"source": "form"}
