from sqlalchemy.orm import Session
from app.database.models import Repository, IndexingJob

def create_repository(
        db:Session,
        repo_url:str
):
    """ create new repo entry in the db """
    repository=Repository(
        name=repo_url.split('/')[-1],
        repo_url=repo_url,
        local_path=""
    )
    db.add(repository)
    db.commit()
    db.refresh(repository)
    return repository

def create_indexing_job(
    db: Session,
    repo_id: int
):
    """
    Create indexing job when ingestion starts
    """

    job = IndexingJob(
        repo_id=repo_id,
        status="PENDING",
        chunks_count=0
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    return job

def update_indexing_job_status(
        repo_id:int,
        status:str,
        db:Session,
        error_message:str=None
):
    """ updates the indexing status of the job"""
    job=(
        db.query(IndexingJob).filter(
            IndexingJob.repo_id==repo_id
        ).first()
    )
    if not job:
       return None
    job.status=status

    if error_message:
        job.error_message=error_message

    db.commit()
    db.refresh(job)
    return job
