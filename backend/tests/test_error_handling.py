from fastapi.testclient import TestClient

from app.core.db import get_db
from app.main import app


def test_unhandled_exception_returns_generic_error_without_leaking_details(db_session, monkeypatch):
    def _boom(db):
        raise RuntimeError("detalhe técnico sensível: senha=123")

    monkeypatch.setattr("app.services.lead_service.list_leads", _boom)

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    # ServerErrorMiddleware sempre relança a exceção original mesmo com um handler
    # registrado; raise_server_exceptions=False replica o comportamento real do
    # uvicorn, onde a resposta 500 genérica já foi enviada ao cliente.
    test_client = TestClient(app, raise_server_exceptions=False)
    try:
        response = test_client.get("/leads")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {"detail": "Erro interno. Tente novamente."}
    assert "senha" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
