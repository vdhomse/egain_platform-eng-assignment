from fastapi import APIRouter, Header, HTTPException, Request
from ..config import Settings
from ..models import DocumentIngestRequest, DocumentIngestResponse
from ..auth import authorize_tenant
from ..metrics import MetricTimer
from ..db import connect
from ..services import ingest_document, audit

router = APIRouter()

def get_settings(request: Request) -> Settings:
    return request.app.state.settings

@router.post("/api/v1/tenants/{tenantId}/documents", response_model=DocumentIngestResponse, status_code=201)
def create_document(
    tenantId: str,
    payload: DocumentIngestRequest,
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    settings = get_settings(request)
    timer = MetricTimer(tenantId, "/api/v1/tenants/{tenantId}/documents", "POST")
    conn = connect(settings.db_path)
    try:
        actor = authorize_tenant(settings, tenantId, x_api_key)
        doc_id = ingest_document(conn, tenantId, payload.title, payload.content, payload.tags)
        audit(conn, tenantId, actor, "document_ingested", {"document_id": doc_id, "title": payload.title, "tags": payload.tags})
        timer.observe(status_code=201, is_error=False)
        return DocumentIngestResponse(document_id=doc_id)
    except HTTPException as e:
        timer.observe(status_code=e.status_code, is_error=True)
        raise
    except Exception as e:
        timer.observe(status_code=500, is_error=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
