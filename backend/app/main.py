from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import ingest, events, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIEM-lite API",
    description="Log ingestion, normalization, and rule + ML-based threat detection.",
    version="0.1.0",
)

# Dev-friendly CORS. Lock this down to specific origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(events.router)
app.include_router(stats.router)


@app.get("/health")
def health():
    return {"status": "ok"}
