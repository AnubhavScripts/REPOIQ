from sqlalchemy import Column,String,Integer
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.sql import func # gives automatic timestamps

from app.database.connection import Base

class Repository(Base):
    __tablename__ = "repositories"
    id= Column(Integer, primary_key=True,index=True)
    name= Column(String,nullable=False)
    repo_url=Column(String,nullable=False)

    local_path = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class IndexingJob(Base):
    __tablename__ ="indexing_jobs"
    id=Column(Integer,primary_key=True,index=True)
    repo_id=Column(Integer,ForeignKey("repositories.id"))
    status=Column(String,nullable=False)
    chunks_count=Column(Integer,default=0)
    error_message=Column(String,nullable=True)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id=Column(Integer, primary_key=True, index=True)
    repo_id = Column(
        Integer,
        ForeignKey("repositories.id")
    )

    title = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id")
    )

    role = Column(String, nullable=False)

    content = Column(Text, nullable=False)

class CodeReview(Base):
    __tablename__ = "code_reviews"
    id = Column(Integer, primary_key=True, index=True)
    repo_id=Column(Integer,ForeignKey("repositories.id"))
    score=Column(Integer)
    review_json = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )