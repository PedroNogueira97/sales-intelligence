import uuid


def test_create_company_returns_201(client):
    response = client.post("/companies", json={"name": "Acme Sales"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Acme Sales"
    assert body["pain_points"] == []
    assert "id" in body


def test_create_company_rejects_empty_name(client):
    response = client.post("/companies", json={"name": ""})

    assert response.status_code == 422


def test_get_company_returns_created_company(client):
    created = client.post(
        "/companies",
        json={"name": "Acme Sales", "average_ticket": 10000, "pain_points": ["perda de leads"]},
    ).json()

    response = client.get(f"/companies/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["average_ticket"] == 10000.0
    assert body["pain_points"] == ["perda de leads"]


def test_get_company_returns_404_when_not_found(client):
    response = client.get(f"/companies/{uuid.uuid4()}")

    assert response.status_code == 404
