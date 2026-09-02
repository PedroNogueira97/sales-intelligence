import logging
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.companies import router as companies_router
from app.api.leads import router as leads_router
from app.core.config import settings
from app.integrations.telegram_polling import run_polling_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    stop_event = threading.Event()
    thread: threading.Thread | None = None
    if settings.telegram_bot_token:
        thread = threading.Thread(target=run_polling_loop, args=(stop_event,), daemon=True)
        thread.start()
        logger.info("Thread de polling do Telegram iniciada.")
    else:
        logger.info("TELEGRAM_BOT_TOKEN não configurado — polling do Telegram desativado.")
    yield
    stop_event.set()
    if thread is not None:
        thread.join(timeout=5)


app = FastAPI(title="Sales Intelligence API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    # MVP local: frontend Vite roda em portas fixas de dev, sem domínio de produção ainda.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(companies_router)
app.include_router(leads_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Defesa em profundidade: qualquer erro não tratado vira 500 genérico.

    O detalhe técnico só vai para o log do servidor — nunca stack trace ao cliente
    (skill backend: "Não retornar stack traces para o cliente").
    """
    logger.error("Erro não tratado em %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Erro interno. Tente novamente."})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
