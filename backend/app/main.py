from fastapi import FastAPI

from app.api.companies import router as companies_router
from app.api.leads import router as leads_router

app = FastAPI(title="Sales Intelligence API")
app.include_router(companies_router)
app.include_router(leads_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
