# pyrefly: ignore [missing-import]
from qdrant_client import QdrantClient
import uuid
# pyrefly: ignore [missing-import]
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from  app.config import settings

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)
def create_collection(vector_size:int):
    """ create collection if not exists"""
    collections=client.get_collections()
    collection_names = [
         c.name
         for c in collections.collections 
    ]
    if settings.QDRANT_COLLECTION not in collection_names:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        client.create_payload_index(
            collection_name=settings.QDRANT_COLLECTION,
            field_name="repo_id",
            field_schema=PayloadSchemaType.INTEGER
        )
def store_vectors(embedded_chunks:list):
    """store embeddded chunks"""
    if not embedded_chunks:
        return
    Vector_size=len(
        embedded_chunks[0]["embedding"]

    )
    create_collection(Vector_size)
    points=[]

    for chunk in embedded_chunks: #helps in increasing the counter index
        point = PointStruct(
           id=str(uuid.uuid4()),
            vector=chunk['embedding'],
            payload={
                "repo_id":chunk['repo_id'],
                "file_path":chunk["file_path"],
                "language":chunk["language"],
                "chunk_text":chunk["chunk_text"]

            }
        )
        points.append(point)
    client.upsert(#update + insert
            collection_name=settings.QDRANT_COLLECTION,
            points=points
        )
def search_vectors(
        repo_id:int,
        query_vector:list,
        limit:int = 5
):
    """ serch the vectors who are similar"""
    result = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="repo_id",
                    match=MatchValue(
                        value=repo_id
                    )
                )
            ]
        ),
        limit=limit
    )
    return result.points