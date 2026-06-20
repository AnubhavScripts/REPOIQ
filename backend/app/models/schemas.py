from pydantic import BaseModel #basemodels is used for data validaton
from typing import List

class Ingestrequest(BaseModel):
    repo_url:str

class IngestResponse(BaseModel):
    repo_id:str
    status : str

class StatusResponse(BaseModel):
    repo_id: str
    status: str
    error_message: str | None = None



class ChatRequest(BaseModel):
    repo_id:str
    question:str

class ChatResponse(BaseModel):
    answer:str



class ReviewRequest(BaseModel):
    repo_id:str

class IssueResponse(BaseModel):
    issue:str
    evidence:str
    impact:str
    recommendation:str
    example_fix:str

class ReviewResponse(BaseModel):
    score:int
    issues:List[IssueResponse]


#this file is used for organisation and introducing reuse concept
#  where we define the schemas in one place and reuse it multiple times