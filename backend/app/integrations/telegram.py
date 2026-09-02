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
    try:
        response = httpx.get(url, params={"offset": offset, "timeout": timeout}, timeout=timeout + 10)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        # a excecao padrao do httpx inclui a URL da requisicao (com o token) na mensagem — nunca
        # deixar isso subir pro log; propaga só o status code.
        raise RuntimeError(
            f"Telegram Bot API respondeu {exc.response.status_code}"
        ) from None
    except httpx.HTTPError as exc:
        # idem: erros de rede do httpx também costumam incluir a URL requisitada na mensagem.
        raise RuntimeError(f"Falha de rede ao chamar a Telegram Bot API: {type(exc).__name__}") from None

    body = response.json()
    if not body.get("ok"):
        # nunca logar o token (esta so na URL, nao no corpo da resposta) — so o payload de erro.
        logger.warning("Resposta inesperada da Telegram Bot API: %s", body)
        return []
    return body.get("result", [])
