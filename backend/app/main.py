from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.api.review import router as review_router 
from app.database.connection import engine
from app.database.models import Base

app= FastAPI(
    title="Repo IQ",
    description="AI Repository analysis and code critic ",
    version = '1.0.0'
)
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_credentials=True,
    allow_methods=['*']
)
app.include_router ( 
    chat_router,
    prefix="/api",
    tags=["chat"]
)
app.include_router (
    ingest_router,
    prefix="/api",
    tags=['ingestion']
)
app.include_router (
    review_router,
    prefix='/api',
    tags=['review']
)
@app.get("/")
def root():
    return {"message":"Backend is running"}
@app.get("/health")
def health_check():
    return {"status":"ok"}