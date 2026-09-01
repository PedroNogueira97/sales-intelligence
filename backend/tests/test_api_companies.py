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


def test_create_second_company_is_rejected(client):
    client.post("/companies", json={"name": "Acme Sales"})

    response = client.post("/companies", json={"name": "Outra Empresa"})

    assert response.status_code == 409


def test_get_company_returns_configured_company(client):
    created = client.post(
        "/companies",
        json={"name": "Acme Sales", "average_ticket": 10000, "pain_points": ["perda de leads"]},
    ).json()

    response = client.get("/companies")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["average_ticket"] == 10000.0
    assert body["pain_points"] == ["perda de leads"]


def test_get_company_returns_404_when_not_configured(client):
    response = client.get("/companies")

    assert response.status_code == 404


def test_update_company_applies_partial_changes(client):
    client.post("/companies", json={"name": "Acme Sales", "communication_tone": "professional"})

    response = client.put("/companies", json={"communication_tone": "casual"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Acme Sales"
    assert body["communication_tone"] == "casual"


def test_update_company_returns_404_when_not_configured(client):
    response = client.put("/companies", json={"communication_tone": "casual"})

    assert response.status_code == 404
