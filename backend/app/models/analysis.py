import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.enums import Intent, Qualification, RecommendedAction


class Analysis(Base):
    """Resultado persistido de uma execução de análise sobre um lead.

    Um lead pode ter mais de uma análise ao longo do tempo (histórico);
    a mais recente é a que representa o estado atual do lead.
    """

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    qualification: Mapped[Qualification] = mapped_column(
        Enum(Qualification, name="qualification", values_callable=lambda e: [item.value for item in e]),
        nullable=False,
    )
    intent: Mapped[Intent] = mapped_column(
        Enum(Intent, name="intent", values_callable=lambda e: [item.value for item in e]),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    pain_points: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")
    reasons: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")
    recommended_action: Mapped[RecommendedAction] = mapped_column(
        Enum(RecommendedAction, name="recommended_action", values_callable=lambda e: [item.value for item in e]),
        nullable=False,
    )
    response: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
