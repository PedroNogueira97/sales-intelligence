import pytest

from app.core.enums import LeadChannel
from app.schemas.company import CompanyCreate
from app.schemas.lead import LandingPageLeadCreate, LeadCreate, WhatsAppLeadCreate
from app.services import company_service, lead_service


def _create_company(db_session, **overrides):
    payload = {"name": "Acme Sales"}
    payload.update(overrides)
    return company_service.create(db_session, CompanyCreate(**payload))


def test_create_lead_manual_sets_manual_channel(db_session):
    _create_company(db_session)

    lead = lead_service.create(
        db_session,
        LeadCreate(name="Joao", email="joao@example.com", message="Preciso de ajuda"),
        channel=LeadChannel.MANUAL,
    )

    assert lead.channel == LeadChannel.MANUAL
    assert lead.email == "joao@example.com"
    assert lead.phone is None


def test_create_lead_whatsapp_sets_whatsapp_channel_without_email(db_session):
    _create_company(db_session)

    lead = lead_service.create(
        db_session,
        WhatsAppLeadCreate(name="Maria", phone="+5511988887777", message="Quero saber mais"),
        channel=LeadChannel.WHATSAPP,
    )

    assert lead.channel == LeadChannel.WHATSAPP
    assert lead.email is None
    assert lead.phone == "+5511988887777"


def test_create_lead_landing_page_sets_landing_page_channel(db_session):
    _create_company(db_session)

    lead = lead_service.create(
        db_session,
        LandingPageLeadCreate(name="Carlos", email="carlos@example.com", message="Interessado"),
        channel=LeadChannel.LANDING_PAGE,
    )

    assert lead.channel == LeadChannel.LANDING_PAGE
    assert lead.email == "carlos@example.com"
    assert lead.phone is None


def test_create_lead_without_company_configured_raises(db_session):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        lead_service.create(
            db_session,
            LeadCreate(name="Joao", email="joao@example.com", message="mensagem"),
            channel=LeadChannel.MANUAL,
        )

    assert exc_info.value.status_code == 422
