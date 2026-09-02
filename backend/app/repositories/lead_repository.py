import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models import Analysis, Lead


def create(db: Session, lead: Lead) -> Lead:
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_by_id(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.get(Lead, lead_id)


def get_by_telegram_chat_id(db: Session, telegram_chat_id: str) -> Lead | None:
    stmt = select(Lead).where(Lead.telegram_chat_id == telegram_chat_id)
    return db.execute(stmt).scalars().first()


def get_latest_analysis(db: Session, lead_id: uuid.UUID) -> Analysis | None:
    stmt = (
        select(Analysis)
        .where(Analysis.lead_id == lead_id)
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalars().first()


def list_with_latest_analysis(db: Session) -> list[tuple[Lead, Analysis | None]]:
    """Todos os leads com sua análise mais recente (se houver), ordenados por score DESC.

    Usa DISTINCT ON (Postgres) para pegar apenas a análise mais recente por lead
    em uma única query, evitando N+1.
    """
    latest_analysis_subq = (
        select(Analysis)
        .distinct(Analysis.lead_id)
        .order_by(Analysis.lead_id, Analysis.created_at.desc())
        .subquery()
    )
    latest_analysis = aliased(Analysis, latest_analysis_subq)

    stmt = (
        select(Lead, latest_analysis)
        .outerjoin(latest_analysis_subq, latest_analysis_subq.c.lead_id == Lead.id)
        .order_by(latest_analysis_subq.c.score.desc().nulls_last())
    )
    return [(lead, analysis) for lead, analysis in db.execute(stmt).all()]
