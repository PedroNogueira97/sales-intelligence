import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class LeadMessage(Base):
    """Histórico de mensagens de um lead (SPEC.md secao 8).

    Distinto de `Interaction`: aqui fica o conteúdo real trocado com o lead, não eventos de
    sistema. `external_message_id` guarda o `update_id` do Telegram — único, evita reprocessar
    a mesma mensagem em caso de restart do polling (SPEC.md secao 10).
    """

    __tablename__ = "lead_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    external_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
