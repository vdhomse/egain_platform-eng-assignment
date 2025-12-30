import os
import tempfile
from fastapi.testclient import TestClient
from app.main import create_app

def make_client():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    os.environ["DB_PATH"] = tmp.name
    os.environ["API_KEYS_JSON"] = '{"tenantA":"keyA","tenantB":"keyB"}'
    app = create_app()
    return TestClient(app)

def test_health():
    c = make_client()
    r = c.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_tenant_auth_required():
    c = make_client()
    r = c.post("/api/v1/tenants/tenantA/documents", json={"title":"t","content":"c","tags":[]})
    assert r.status_code == 401

def test_ingest_and_search_isolated():
    c = make_client()

    ra = c.post(
        "/api/v1/tenants/tenantA/documents",
        headers={"X-API-Key":"keyA"},
        json={"title":"A1","content":"hello knowledge base", "tags":["x"]},
    )
    assert ra.status_code == 201
    docA = ra.json()["document_id"]

    rb = c.post(
        "/api/v1/tenants/tenantB/documents",
        headers={"X-API-Key":"keyB"},
        json={"title":"B1","content":"hello knowledge base", "tags":["y"]},
    )
    assert rb.status_code == 201
    docB = rb.json()["document_id"]
    assert docA != docB

    sa = c.get(
        "/api/v1/tenants/tenantA/documents/search",
        headers={"X-API-Key":"keyA"},
        params={"q":"knowledge", "limit":10, "offset":0},
    )
    assert sa.status_code == 200
    idsA = [x["document_id"] for x in sa.json()["results"]]
    assert docA in idsA
    assert docB not in idsA

    sb = c.get(
        "/api/v1/tenants/tenantB/documents/search",
        headers={"X-API-Key":"keyB"},
        params={"q":"knowledge", "limit":10, "offset":0},
    )
    assert sb.status_code == 200
    idsB = [x["document_id"] for x in sb.json()["results"]]
    assert docB in idsB
    assert docA not in idsB

def test_metrics_shape():
    c = make_client()
    c.get("/api/v1/health")
    m = c.get("/api/v1/metrics")
    assert m.status_code == 200
    j = m.json()
    for k in ["request_count_per_tenant","avg_response_time_ms_per_tenant","document_count_per_tenant","error_rate_per_tenant"]:
        assert k in j
