from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


@lru_cache
def get_llm() -> BaseChatModel:
    """Cria o chat model configurado via env (`LLM_PROVIDER`/`LLM_MODEL`/`LLM_API_KEY`).

    Isolado nesta função para trocar de provedor sem tocar nos nodes do grafo
    (skill langgraph: "Não acoplar o código inteiro a um único fornecedor").
    """
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            timeout=30,
        )

    raise ValueError(f"Provedor de LLM não suportado: {settings.llm_provider!r}")
