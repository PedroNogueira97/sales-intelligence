from app.core.enums import LeadChannel
from app.integrations.telegram_polling import process_update
from app.models import Lead, LeadMessage
from app.repositories import lead_message_repository, lead_repository
from app.schemas.company import CompanyCreate
from app.services import company_service


def _create_company(db_session, **overrides):
    payload = {"name": "Acme Sales"}
    payload.update(overrides)
    return company_service.create(db_session, CompanyCreate(**payload))


def _update(update_id: int, chat_id: int, text: str, first_name: str = "Maria") -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "from": {"id": chat_id, "is_bot": False, "first_name": first_name},
            "chat": {"id": chat_id, "first_name": first_name, "type": "private"},
            "date": 1690000000,
            "text": text,
        },
    }


def test_process_update_ignores_updates_without_text(db_session):
    _create_company(db_session)
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 111, "is_bot": False, "first_name": "Maria"},
            "chat": {"id": 111, "type": "private"},
            "date": 1690000000,
            "sticker": {"file_id": "abc"},
        },
    }

    process_update(db_session, update)

    assert lead_repository.get_by_telegram_chat_id(db_session, "111") is None


def test_process_update_creates_new_lead_by_chat_id(db_session):
    _create_company(db_session)
    update = _update(1, 987654321, "Oi, tenho interesse no produto de voces", first_name="Bruna")

    process_update(db_session, update)

    lead = lead_repository.get_by_telegram_chat_id(db_session, "987654321")
    assert lead is not None
    assert lead.name == "Bruna"
    assert lead.channel == LeadChannel.TELEGRAM
    assert lead.message == "Oi, tenho interesse no produto de voces"

    messages = lead_message_repository.list_by_lead(db_session, lead.id)
    assert len(messages) == 1
    assert messages[0].external_message_id == "1"


def test_process_update_appends_message_to_existing_lead_by_chat_id(db_session):
    company = _create_company(db_session)
    lead = Lead(
        company_id=company.id,
        channel=LeadChannel.TELEGRAM,
        telegram_chat_id="555",
        name="Joao",
        message="primeira mensagem",
    )
    lead_repository.create(db_session, lead)
    lead_message_repository.create(
        db_session,
        LeadMessage(lead_id=lead.id, content="primeira mensagem", external_message_id="10"),
    )

    process_update(db_session, _update(11, 555, "segunda mensagem"))

    messages = lead_message_repository.list_by_lead(db_session, lead.id)
    assert len(messages) == 2
    assert messages[1].content == "segunda mensagem"
    # não deve criar um segundo lead para o mesmo chat_id
    assert lead_repository.get_by_telegram_chat_id(db_session, "555").id == lead.id


def test_process_update_is_idempotent_by_external_message_id(db_session):
    _create_company(db_session)
    update = _update(42, 222, "mensagem repetida")

    process_update(db_session, update)
    process_update(db_session, update)

    lead = lead_repository.get_by_telegram_chat_id(db_session, "222")
    messages = lead_message_repository.list_by_lead(db_session, lead.id)
    assert len(messages) == 1


def test_process_update_skips_when_no_company_configured(db_session):
    process_update(db_session, _update(1, 333, "oi"))

    assert lead_repository.get_by_telegram_chat_id(db_session, "333") is None
