import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import ReviewRequest, ReviewResponse
from app.services.embedding_Service import embed_query
from app.services.llm_service import _call_groq, FAST_MODEL, SMART_MODEL
from app.vectorstore.qdrant_Service import search_vectors

router = APIRouter()

# ---------------------------------------------------------------------------
# Search helper — each agent uses targeted queries to get relevant chunks only
# ---------------------------------------------------------------------------

def _search(repo_id: int, queries: list[str], limit: int = 5) -> str:
    """
    Run multiple targeted Qdrant searches and concatenate unique results.
    This keeps each agent's context small and focused.
    """
    seen = set()
    chunks = []
    for query in queries:
        vector = embed_query(query)
        results = search_vectors(repo_id=repo_id, query_vector=vector, limit=limit)
        for r in results:
            text = r.payload.get("chunk_text", "")
            file_path = r.payload.get("file_path", "")
            key = text[:100]  # dedup by first 100 chars
            if key not in seen:
                seen.add(key)
                chunks.append(f"### {file_path}\n{text}")
    return "\n\n".join(chunks) if chunks else "No relevant code found."


# ---------------------------------------------------------------------------
# Individual Agents — each runs ONE focused Groq call on targeted chunks
# ---------------------------------------------------------------------------

EVIDENCE_RULE = (
    "\nCRITICAL: Only report issues you can see direct evidence of in the code above. "
    "If you cannot find evidence, say 'Insufficient context to evaluate.' "
    "Do NOT assume or guess issues that aren't visible. "
    "Cite the file name for every issue you find.\n"
)

def _security_agent(repo_id: int) -> dict:
    context = _search(repo_id, [
        "authentication authorization token secret password api_key",
        "CORS allow_origins middleware headers",
        "SQL query database raw input",
        "environment variable hardcoded credentials",
    ])
    prompt = f"""You are a brutal security engineer doing a red-team review.

Code Context:
{context}
{EVIDENCE_RULE}
Find security vulnerabilities: hardcoded secrets, open CORS, missing auth, SQL injection risks, 
exposed env vars, no rate limiting, missing input validation.

Respond in this exact JSON format:
{{
  "score": <integer 1-10 where 10 is perfect security>,
  "issues": [
    {{
      "issue": "<issue title>",
      "evidence": "<exact file + what you saw>",
      "impact": "<what an attacker could do>",
      "recommendation": "<how to fix it>",
      "example_fix": "<one line code example if possible>"
    }}
  ]
}}
If no issues found, return an empty issues array with a high score."""

    raw = _call_groq(prompt, model=FAST_MODEL)
    return _parse_agent_json(raw, "Security")


def _performance_agent(repo_id: int) -> dict:
    context = _search(repo_id, [
        "async await synchronous blocking request",
        "loop query database N+1 fetch",
        "embedding generation batch processing",
        "pagination limit offset large data",
    ])
    prompt = f"""You are a brutal performance engineer reviewing this codebase.

Code Context:
{context}
{EVIDENCE_RULE}
Find performance issues: blocking I/O on request threads, N+1 queries, 
missing pagination, no caching, large in-memory operations, synchronous where async is needed.

Respond in this exact JSON format:
{{
  "score": <integer 1-10 where 10 is perfect performance>,
  "issues": [
    {{
      "issue": "<issue title>",
      "evidence": "<exact file + what you saw>",
      "impact": "<how bad this gets under load>",
      "recommendation": "<how to fix it>",
      "example_fix": "<one line code example if possible>"
    }}
  ]
}}"""

    raw = _call_groq(prompt, model=FAST_MODEL)
    return _parse_agent_json(raw, "Performance")


def _architecture_agent(repo_id: int) -> dict:
    context = _search(repo_id, [
        "class module import structure separation",
        "router endpoint handler service layer",
        "global variable singleton module level",
        "error handling exception try catch",
    ])
    prompt = f"""You are a brutal software architect reviewing this codebase.

Code Context:
{context}
{EVIDENCE_RULE}
Find architecture problems: god functions, missing separation of concerns, 
module-level side effects, poor error handling, missing abstractions, 
business logic mixed with API layer.

Respond in this exact JSON format:
{{
  "score": <integer 1-10 where 10 is perfect architecture>,
  "issues": [
    {{
      "issue": "<issue title>",
      "evidence": "<exact file + what you saw>",
      "impact": "<how this causes bugs or slows development>",
      "recommendation": "<how to fix it>",
      "example_fix": "<one line code example if possible>"
    }}
  ]
}}"""

    raw = _call_groq(prompt, model=FAST_MODEL)
    return _parse_agent_json(raw, "Architecture")


def _scalability_agent(repo_id: int) -> dict:
    context = _search(repo_id, [
        "state session volume file local disk",
        "single instance stateful memory cache",
        "background task queue worker",
        "config environment deployment docker",
    ])
    prompt = f"""You are a brutal DevOps and scalability engineer reviewing this codebase.

Code Context:
{context}
{EVIDENCE_RULE}
Find scalability problems: stateful design that breaks with multiple instances,
local disk usage that won't work in containers, no job queue for heavy tasks,
missing caching, single points of failure.

Respond in this exact JSON format:
{{
  "score": <integer 1-10 where 10 is perfectly scalable>,
  "issues": [
    {{
      "issue": "<issue title>",
      "evidence": "<exact file + what you saw>",
      "impact": "<how this breaks when you scale to 2+ instances>",
      "recommendation": "<how to fix it>",
      "example_fix": "<one line code example if possible>"
    }}
  ]
}}"""

    raw = _call_groq(prompt, model=FAST_MODEL)
    return _parse_agent_json(raw, "Scalability")


def _verdict_agent(security: dict, performance: dict, architecture: dict, scalability: dict) -> str:
    """Final brutal verdict synthesising all 4 agent reports using the smart model."""
    summary = f"""
SECURITY REPORT (score: {security.get('score', '?')}/10):
Issues found: {len(security.get('issues', []))}
{_format_issues(security.get('issues', []))}

PERFORMANCE REPORT (score: {performance.get('score', '?')}/10):
Issues found: {len(performance.get('issues', []))}
{_format_issues(performance.get('issues', []))}

ARCHITECTURE REPORT (score: {architecture.get('score', '?')}/10):
Issues found: {len(architecture.get('issues', []))}
{_format_issues(architecture.get('issues', []))}

SCALABILITY REPORT (score: {scalability.get('score', '?')}/10):
Issues found: {len(scalability.get('issues', []))}
{_format_issues(scalability.get('issues', []))}
"""

    prompt = f"""You are the most honest, brutal senior engineer in the world. 
You have just received specialist reports on a codebase. 
You do not sugarcoat. You do not encourage people falsely. 
You speak like a staff engineer who will have to maintain this code.

{summary}

Write a brutal but fair final verdict. Include:
1. An overall score out of 10 (average of the 4 scores, rounded).
2. A 2-3 sentence brutal overall assessment — what is the real state of this codebase.
3. The single most critical thing to fix RIGHT NOW.
4. A "Would you hire the dev who wrote this?" answer with reasoning.
5. Any genuine green flags — things done correctly (if any).

Be direct. No filler. No "great start though!". If it's bad, say it's bad."""

    return _call_groq(prompt, model=SMART_MODEL)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_agent_json(raw: str, agent_name: str) -> dict:
    """Extract JSON from LLM response, with graceful fallback."""
    try:
        # find first { ... } block
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    # fallback — return a structured error
    return {
        "score": 0,
        "issues": [{
            "issue": f"{agent_name} agent parse error",
            "evidence": "Could not parse LLM response",
            "impact": "Unknown",
            "recommendation": "Re-run the review",
            "example_fix": ""
        }]
    }


def _format_issues(issues: list) -> str:
    if not issues:
        return "  No issues found."
    return "\n".join(
        f"  - [{i['issue']}] in {i.get('evidence', 'unknown')} → {i.get('impact', '')}"
        for i in issues
    )


def _overall_score(security, performance, architecture, scalability) -> int:
    scores = [
        security.get("score", 5),
        performance.get("score", 5),
        architecture.get("score", 5),
        scalability.get("score", 5),
    ]
    return round(sum(scores) / len(scores))


# ---------------------------------------------------------------------------
# API Endpoint
# ---------------------------------------------------------------------------

@router.post("/review")
def review_repository(
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Multi-agent brutal code review.
    Runs 4 specialist agents in parallel (security, performance, architecture, scalability)
    then synthesises a final brutal verdict.
    """
    repo_id = int(request.repo_id)

    # Run all 4 agents in parallel using a thread pool
    # (Groq calls are blocking/sync, so we use threads not asyncio)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_security     = executor.submit(_security_agent,     repo_id)
        future_performance  = executor.submit(_performance_agent,  repo_id)
        future_architecture = executor.submit(_architecture_agent, repo_id)
        future_scalability  = executor.submit(_scalability_agent,  repo_id)

        try:
            security     = future_security.result(timeout=60)
            performance  = future_performance.result(timeout=60)
            architecture = future_architecture.result(timeout=60)
            scalability  = future_scalability.result(timeout=60)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Final synthesis — one smart model call
    try:
        verdict = _verdict_agent(security, performance, architecture, scalability)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verdict agent error: {str(e)}")

    return {
        "overall_score": _overall_score(security, performance, architecture, scalability),
        "verdict": verdict,
        "security":     security,
        "performance":  performance,
        "architecture": architecture,
        "scalability":  scalability,
    }