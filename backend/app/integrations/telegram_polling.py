"""Loop de long polling do Telegram (SPEC.md secao 10).

Roda em background thread (nao asyncio task — o resto do codebase e sincrono/SQLAlchemy
classico), com o offset guardado em memoria (nao persistido: reinicia do zero a cada restart do
processo, aceitavel pra este MVP — ver SPEC.md secao 10). A idempotencia real contra
reprocessamento vem do indice unico em `lead_messages.external_message_id`, nao do offset.
"""

import logging
import threading

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.enums import InteractionType, LeadChannel, LeadStatus
from app.integrations.telegram import get_updates
from app.models import Interaction, Lead, LeadMessage
from app.repositories import company_repository, lead_message_repository, lead_repository

logger = logging.getLogger(__name__)


def process_update(db: Session, update: dict) -> None:
    """Processa um unico update do Telegram. Nunca dispara analise automaticamente."""
    message = update.get("message")
    if not message or "text" not in message:
        return  # ignora updates sem mensagem de texto (foto, sticker, edicao, etc.)

    external_message_id = str(update["update_id"])
    if lead_message_repository.get_by_external_id(db, external_message_id) is not None:
        return  # ja processado — defesa extra alem do offset em memoria

    chat_id = str(message["chat"]["id"])
    text = message["text"]
    first_name = message.get("from", {}).get("first_name") or "Lead do Telegram"

    lead = lead_repository.get_by_telegram_chat_id(db, chat_id)
    if lead is not None:
        lead_message_repository.create(
            db,
            LeadMessage(lead_id=lead.id, content=text, external_message_id=external_message_id),
        )
        return

    company = company_repository.get_singleton(db)
    if company is None:
        # sem empresa configurada ainda nao ha contexto pra analisar leads — ignora a mensagem
        # em vez de crashar o loop de polling (nao loga o conteudo, so o fato).
        logger.warning("Mensagem do Telegram recebida sem empresa configurada, ignorando.")
        return

    lead = Lead(
        status=LeadStatus.NEW,
        company_id=company.id,
        channel=LeadChannel.TELEGRAM,
        telegram_chat_id=chat_id,
        name=first_name,
        message=text,
    )
    lead_repository.create(db, lead)
    db.add(Interaction(lead_id=lead.id, type=InteractionType.LEAD_CREATED, payload=None))
    db.commit()
    lead_message_repository.create(
        db, LeadMessage(lead_id=lead.id, content=text, external_message_id=external_message_id)
    )


def run_polling_loop(stop_event: threading.Event) -> None:
    offset = 0
    logger.info("Polling do Telegram iniciado.")
    while not stop_event.is_set():
        try:
            updates = get_updates(offset)
        except Exception as exc:
            logger.warning("Falha ao buscar updates do Telegram: %s", exc)
            stop_event.wait(5)
            continue

        db = SessionLocal()
        try:
            for update in updates:
                try:
                    process_update(db, update)
                except Exception as exc:
                    # um update malformado nao pode travar o loop pra sempre — loga e segue,
                    # avancando o offset (external_message_id garante que nada duplica se um
                    # reprocessamento acontecer por outro motivo).
                    logger.error(
                        "Falha ao processar update do Telegram (update_id=%s): %s",
                        update.get("update_id"),
                        exc,
                    )
                finally:
                    offset = update["update_id"] + 1
        finally:
            db.close()

    logger.info("Polling do Telegram encerrado.")
