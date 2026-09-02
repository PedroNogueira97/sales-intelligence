import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.telegram.org"


def get_updates(offset: int, timeout: int = 30) -> list[dict]:
    """Busca novos updates via long polling (SPEC.md secao 10) — sem webhook, sem URL publica.

    `timeout` e o tempo (em segundos) que a propria Telegram Bot API mantem a conexao aberta
    esperando por novidade antes de responder vazio; o timeout do cliente HTTP precisa ser maior
    que isso pra nao cortar a conexao antes da resposta do servidor.
    """
    url = f"{_BASE_URL}/bot{settings.telegram_bot_token}/getUpdates"
    response = httpx.get(url, params={"offset": offset, "timeout": timeout}, timeout=timeout + 10)
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        # nunca logar o token (esta so na URL, nao no corpo da resposta) — so o payload de erro.
        logger.warning("Resposta inesperada da Telegram Bot API: %s", body)
        return []
    return body.get("result", [])
