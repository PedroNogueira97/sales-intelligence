from fastapi import FastAPI

from app.api.companies import router as companies_router

app = FastAPI(title="Sales Intelligence API")
app.include_router(companies_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
