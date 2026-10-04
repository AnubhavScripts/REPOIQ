import os
import shutil
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.api.review import router as review_router
from app.database.connection import engine
from app.database.models import Base
from app.config import settings

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

@app.on_event("startup")
def cleanup_stale_temp_repos():
    """
    On startup, delete any leftover cloned repos older than 1 hour.
    These are from previous runs that crashed mid-ingestion.
    """
    temp_path = settings.TEMP_REPO_PATH
    if not os.path.exists(temp_path):
        return
    now = time.time()
    one_hour = 3600
    for name in os.listdir(temp_path):
        full = os.path.join(temp_path, name)
        if os.path.isdir(full):
            age = now - os.path.getmtime(full)
            if age > one_hour:
                try:
                    shutil.rmtree(full)
                    print(f"[startup] Cleaned stale temp repo: {name}")
                except Exception as e:
                    print(f"[startup] Failed to clean {name}: {e}")

@app.get("/")
def root():
    return {"message":"Backend is running"}

@app.get("/health")
def health_check():
    return {"status":"ok"}