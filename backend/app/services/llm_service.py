# pyrefly: ignore [missing-import]
from groq import Groq

from app.config import settings

client= Groq(
    api_key=settings.GROQ_API_KEY
)
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

    prompt=build_prompt(
        context_chunks,question
    )
    response= client.chat.completions.create(
        model =settings.GROQ_MODEL,
        messages= [
            {
                "role":"user",
                "content":prompt
            }
        ], 
        temperature = 0.2 #controls the randomness


    )
    return response.choices[0].message.content