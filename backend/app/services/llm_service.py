# pyrefly: ignore [missing-import]
from groq import Groq
import time

from app.config import settings

client= Groq(
    api_key=settings.GROQ_API_KEY
)

# Use a fast small model for sub-agents to save tokens & avoid rate limits
FAST_MODEL = "llama-3.1-8b-instant"
SMART_MODEL = settings.GROQ_MODEL  # llama-3.3-70b-versatile for final verdict


def _call_groq(prompt: str, model: str, retries: int = 3) -> str:
    """
    Call Groq with exponential backoff on rate limit errors (429).
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"Groq rate limit hit — retrying in {wait}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise
    raise Exception("Groq rate limit exceeded after all retries. Try again in a moment.")


def build_prompt(
        context_chunks:list,
        question:str
):
    """ prompt for the model"""
    context= "\n\n".join(context_chunks)
    prompt = f"""
You are Repo IQ, an expert software architect.

Analyze the provided repository code context carefully.

Repository Context:

{context}

User Question:

{question}

Rules:

1. Answer only using provided code context.
2. Mention file relationships when relevant.
3. If context is insufficient, say information is insufficient.
4. Explain technically and clearly.
"""

    return prompt

def generate_response(
        context_chunks:list,
        question:str
):
    """ generate response from groq"""
    prompt = build_prompt(context_chunks, question)
    return _call_groq(prompt, model=SMART_MODEL)