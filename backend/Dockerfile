# ---- Stage 1: install dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: lean runtime image ----
FROM python:3.11-slim

WORKDIR /app

# copy installed packages from builder
COPY --from=builder /install /usr/local

# git is needed at runtime (github_service.py clones repos)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY . .

# directory where repos are temporarily cloned
RUN mkdir -p /app/temp_repos

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
