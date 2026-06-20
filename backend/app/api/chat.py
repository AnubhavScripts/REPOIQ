from fastapi import APIRouter

from app.models.schemas import (
    ChatRequest,ChatResponse
)
from app.services.embedding_Service import (embed_query)
from app.vectorstore.qdrant_Service import (search_vectors)
from app.services.llm_service import (generate_response)
router = APIRouter()

@router.post("/chat",
             response_model=ChatResponse
             )
def  chat_with_repository(
    request:ChatRequest
):
    """ ask questions about repository"""
    
    print(f"--- CHAT DEBUG: received repo_id='{request.repo_id}' (type={type(request.repo_id)}), question='{request.question}' ---")
    
    query_vector=embed_query(
        request.question
    )
    
    received_similar_chunks=search_vectors(
        repo_id=int(request.repo_id),
        query_vector=query_vector
    )
    
    print(f"--- CHAT DEBUG: search_vectors returned {len(received_similar_chunks)} chunks ---")
    
    context_chunks=[]

    for result in received_similar_chunks:
        context_chunks.append(
            result.payload['chunk_text']
        )
    answer=generate_response(
        context_chunks=context_chunks,
        question=request.question
    )
    return ChatResponse(
        answer=answer,
    )