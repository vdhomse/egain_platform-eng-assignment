# eGain Knowledge Indexing Service (Assignment)

Implements **Part 2** requirements:
- Document ingestion
- Tenant-isolated text search
- Health and metrics endpoints
- Proper indexing using SQLite FTS5

Uses **FastAPI** + **SQLite (FTS5)** for a minimal, easy-to-run local setup.

## Quickstart

### 1. Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export API_KEYS_JSON='{"tenantA":"keyA","tenantB":"keyB"}'
uvicorn app.main:app --reload --port 8000
```

## Features Implemented

### Feature 1: Document Ingestion API
- `POST /api/v1/tenants/{tenantId}/documents`
- Accepts document metadata (`title`, `content`, `tags`)
- Validates tenant authorization via API key
- Ensures tenant data isolation
- Generates a unique document ID
- Returns `201 Created` with document ID

### Feature 2: Search API
- `GET /api/v1/tenants/{tenantId}/documents/search`
- Full-text search scoped to a tenant
- Pagination via `limit` and `offset`
- Ranked results with relevance scores (BM25)
- Enforces tenant data isolation

### Feature 3: Metrics & Health
- `GET /api/v1/health` for load balancers
- `GET /api/v1/metrics` exposing:
  - Request count per tenant
  - Average response time per tenant
  - Document count per tenant
  - Error rates per tenant

## Endpoints

### Health
```bash
curl -s http://localhost:8000/api/v1/health
```

### Ingest (tenantA)
```bash
curl -X POST \
  -H "X-API-Key: keyA" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/v1/tenants/tenantA/documents \
  -d '{
    "title": "My doc",
    "content": "This is a sample document about customer experience and knowledge bases.",
    "tags": ["kb","cx"]
  }'
```


### Search (tenantA)
```bash
curl -s   -H "X-API-Key: keyA"   "http://localhost:8000/api/v1/tenants/tenantA/documents/search?q=knowledge&limit=10&offset=0"
```

### Metrics (JSON)
```bash
curl -s http://localhost:8000/api/v1/metrics | python -m json.tool
```

## Running Tests
```bash
pytest --cov=app
```

## Benchmark
```bash
python scripts/benchmark.py
```

## API Documentation (OpenAPI / Swagger)

FastAPI automatically generates interactive API documentation:

- Swagger UI:  
  http://localhost:8000/docs

- OpenAPI specification:  
  http://localhost:8000/openapi.json

## Indexing & Search Performance

Search is backed by **SQLite FTS5**, which builds an inverted index inside the SQLite database file.
Queries use BM25 ranking and are scoped by `tenant_id`, enabling efficient full-text search with
sub-100ms latency for datasets up to ~10K documents in local benchmarks.

---

## Technology Stack

- **Language / Framework:** Python, FastAPI
- **Storage:** SQLite (file-backed by default)
- **Search Index:** SQLite FTS5 (BM25 ranking)
- **Authentication:** Simplified API key per tenant
- **Metrics:** In-memory counters + optional Prometheus
- **Testing:** pytest

> **Note:**  
> The assignment implementation uses SQLite and an in-process execution model to keep local setup simple.  
> In production, the same APIs would be backed by MySQL, Amazon OpenSearch, and Amazon SQS.

---


