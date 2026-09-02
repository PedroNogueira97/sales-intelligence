from unittest.mock import patch

import httpx
import pytest

from app.core.config import settings
from app.integrations.telegram import get_updates


def test_get_updates_returns_parsed_results():
    fake_response = httpx.Response(
        200,
        json={"ok": True, "result": [{"update_id": 1}]},
        request=httpx.Request("GET", "https://api.telegram.org/botFAKE/getUpdates"),
    )
    with patch("app.integrations.telegram.httpx.get", return_value=fake_response):
        assert get_updates(0) == [{"update_id": 1}]


def test_get_updates_never_leaks_token_when_telegram_returns_an_error(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "SECRET_TOKEN_12345")
    request = httpx.Request(
        "GET", f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
    )
    fake_response = httpx.Response(409, json={"ok": False}, request=request)
    with patch("app.integrations.telegram.httpx.get", return_value=fake_response):
        with pytest.raises(RuntimeError) as exc_info:
            get_updates(0)

    assert "SECRET_TOKEN_12345" not in str(exc_info.value)
    assert "409" in str(exc_info.value)


def test_get_updates_never_leaks_token_on_network_error(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "SECRET_TOKEN_12345")

    def _raise(*args, **kwargs):
        request = httpx.Request(
            "GET", f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
        )
        raise httpx.ConnectError("connection refused", request=request)

    with patch("app.integrations.telegram.httpx.get", side_effect=_raise):
        with pytest.raises(RuntimeError) as exc_info:
            get_updates(0)

    assert "SECRET_TOKEN_12345" not in str(exc_info.value)
