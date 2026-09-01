from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.companies import router as companies_router
from app.api.leads import router as leads_router

app = FastAPI(title="Sales Intelligence API")
app.add_middleware(
    CORSMiddleware,
    # MVP local: frontend Vite roda em portas fixas de dev, sem domínio de produção ainda.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(companies_router)
app.include_router(leads_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
