from fastapi import APIRouter,Depends,BackgroundTasks,HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import Ingestrequest,IngestResponse,StatusResponse
from app.database.connection import get_db,SessionLocal
from app.services.github_service import clone_repository, delete_repository
from app.services.parser_service import parse_repository
from app.services.chunk_service import chunk_repository_files
from app.services.embedding_Service import generate_embeddings
from app.vectorstore.qdrant_Service import store_vectors
from app.database.crud import (
    create_repository,
    create_indexing_job,
    update_indexing_job_status,
    get_job_status
)
router = APIRouter()


def process_repository(
        repo_id:int,
        repo_url:str

):
  print("BACKGROUND TASK STARTED")
  """ background task for full repository pipeline """
  db = SessionLocal()
  try:
    update_indexing_job_status(
      db=db,
      repo_id=repo_id,
      status="PROCESSING"
    )
    local_path=clone_repository(repo_url)

    parsed_file=parse_repository(local_path)

    chunk=chunk_repository_files(
      repo_id=repo_id,
      parsed_files=parsed_file)                           
     
    embedded_chunks=generate_embeddings(chunk)
    
    store_vectors(embedded_chunks)
    update_indexing_job_status(
      db=db,
      repo_id=repo_id,
      status="COMPLETED"
    )
  except Exception as e:
    print("BACKGROUND ERROR:", e)
    update_indexing_job_status(
      db=db,
      repo_id=repo_id,
      status="FAILED",
      error_message=str(e)
    )
  finally:
    db.close()
    if 'local_path' in locals() and local_path:
      delete_repository(local_path)

@router.post(
  "/ingest",
  response_model=IngestResponse
)
def ingest_repository(
  request:Ingestrequest,
  background_tasks:BackgroundTasks,
  db:Session= Depends(get_db) #fast api call the get_db and gives session automatically  using dependency injection
):
  try:
    repository=create_repository(
      db=db,
      repo_url=request.repo_url
    )
    create_indexing_job(
      db=db,
      repo_id=repository.id
    )
    print("Scheduling background task")
    background_tasks.add_task(
      process_repository,repository.id,request.repo_url
    )
    return IngestResponse(
      repo_id=str(repository.id),
      status="PENDING"
    )
  except Exception as e:
       print("BACKGROUND ERROR:", e)
       raise HTTPException (
          status_code=500,
          detail=str(e)
       )
@router.get(
  "/status/{repo_id}",
  response_model=StatusResponse
)
def get_status(
  repo_id: int,
  db: Session = Depends(get_db)
):
  """ poll the indexing job status for a given repo """
  job = get_job_status(db=db, repo_id=repo_id)
  if not job:
    raise HTTPException(status_code=404, detail="No indexing job found for this repo")
  return StatusResponse(
    repo_id=str(repo_id),
    status=job.status,
    error_message=job.error_message
  )


