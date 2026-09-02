import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeadMessage


def create(db: Session, lead_message: LeadMessage) -> LeadMessage:
    db.add(lead_message)
    db.commit()
    db.refresh(lead_message)
    return lead_message


def list_by_lead(db: Session, lead_id: uuid.UUID) -> list[LeadMessage]:
    stmt = (
        select(LeadMessage)
        .where(LeadMessage.lead_id == lead_id)
        .order_by(LeadMessage.created_at.asc())
    )
    return list(db.execute(stmt).scalars().all())


def get_by_external_id(db: Session, external_message_id: str) -> LeadMessage | None:
    stmt = select(LeadMessage).where(LeadMessage.external_message_id == external_message_id)
    return db.execute(stmt).scalars().first()
