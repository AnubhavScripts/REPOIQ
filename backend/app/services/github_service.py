import os
import shutil 
import uuid
# pyrefly: ignore [missing-import] #since we are using venv and pyrefly is scanning the gloval env so
#it was showing this import error , following prompt remove the error from the ui 
from git import Repo

from app.config import settings

def clone_repository(repo_url:str) -> str:
    """ Clones Github repo and returns local path """

    repo_name=repo_url.rstrip("/").split("/")[-1]
    unique_name = f"{repo_name}_{uuid.uuid4().hex[:8]}"

    os.makedirs(
        settings.TEMP_REPO_PATH,
        exist_ok=True
    )
    local_path=os.path.join(
        settings.TEMP_REPO_PATH,
        unique_name
    )
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    try:
        Repo.clone_from(repo_url,local_path)
    except Exception as e :
        raise Exception(f"failed to clone the repository: {e}")
    return local_path

def delete_repository(
        localpath:str
):
    """deleting the cloned repo after processing"""
    if os.path.exists(localpath):
        shutil.rmtree(localpath)