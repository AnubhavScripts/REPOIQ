# pyrefly: ignore [missing-import]
from google import genai

from app.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_single_embedding(text: str):
    """
    Generate embedding for one code chunk
    """

    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values

def generate_embeddings(chunks:list):
    """generate embedding for all chunks"""
    embedded_chunks=[]
    for chunk in chunks:

        vector = generate_single_embedding(
            chunk["chunk_text"]
        )

        embedded_chunks.append(
            {
                "repo_id": chunk["repo_id"],
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "chunk_text": chunk["chunk_text"],
                "embedding": vector
            }
        )

    return embedded_chunks
def embed_query(question: str):
    """
    Generate embedding for user question
    """

    result =client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=question
    )

    return result.embeddings[0].values