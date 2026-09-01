import uuid

from app.core.enums import Intent, InteractionType, Qualification, RecommendedAction
from app.models import Analysis, Interaction, Lead


def _create_company(client, **overrides):
    payload = {"name": "Acme Sales"}
    payload.update(overrides)
    return client.post("/companies", json=payload).json()


def test_create_lead_sets_new_status_and_records_interaction(client, db_session):
    company = _create_company(client)

    response = client.post(
        "/leads",
        json={
            "company_id": company["id"],
            "name": "Joao",
            "email": "joao@example.com",
            "company_name": "Prospect LTDA",
            "message": "Preciso de ajuda com meus leads",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "new"

    interactions = (
        db_session.query(Interaction).filter(Interaction.lead_id == uuid.UUID(body["id"])).all()
    )
    assert len(interactions) == 1
    assert interactions[0].type == InteractionType.LEAD_CREATED


def test_create_lead_rejects_unknown_company(client):
    response = client.post(
        "/leads",
        json={
            "company_id": str(uuid.uuid4()),
            "name": "Joao",
            "email": "joao@example.com",
            "message": "mensagem",
        },
    )

    assert response.status_code == 404


def test_get_lead_returns_null_analysis_when_not_analyzed(client):
    company = _create_company(client)
    created = client.post(
        "/leads",
        json={"company_id": company["id"], "name": "Joao", "email": "joao@example.com", "message": "msg"},
    ).json()

    response = client.get(f"/leads/{created['id']}")

    assert response.status_code == 200
    assert response.json()["analysis"] is None


def test_get_lead_returns_404_when_not_found(client):
    response = client.get(f"/leads/{uuid.uuid4()}")

    assert response.status_code == 404


def test_list_leads_orders_by_score_desc_with_unanalyzed_last(client, db_session):
    company_id = uuid.UUID(_create_company(client)["id"])

    lead_low = Lead(company_id=company_id, name="Low", email="low@example.com", message="m")
    lead_high = Lead(company_id=company_id, name="High", email="high@example.com", message="m")
    lead_unanalyzed = Lead(company_id=company_id, name="None", email="none@example.com", message="m")
    db_session.add_all([lead_low, lead_high, lead_unanalyzed])
    db_session.commit()

    db_session.add_all(
        [
            Analysis(
                lead_id=lead_low.id,
                score=20,
                qualification=Qualification.UNQUALIFIED,
                intent=Intent.LOW,
                confidence=0.5,
                pain_points=[],
                reasons=["motivo"],
                recommended_action=RecommendedAction.DISCARD,
            ),
            Analysis(
                lead_id=lead_high.id,
                score=90,
                qualification=Qualification.QUALIFIED,
                intent=Intent.HIGH,
                confidence=0.9,
                pain_points=[],
                reasons=["motivo"],
                recommended_action=RecommendedAction.SCHEDULE_DEMO,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/leads")

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["High", "Low", "None"]
