from sqlalchemy.orm import Session

from app.models import Analysis


def create(db: Session, analysis: Analysis) -> Analysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
