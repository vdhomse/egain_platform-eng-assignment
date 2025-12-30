from fastapi import APIRouter, Header, HTTPException, Request
from ..config import Settings
from ..models import SearchResponse, SearchResultItem
from ..auth import authorize_tenant
from ..metrics import MetricTimer
from ..db import connect
from ..services import search_documents, audit

router = APIRouter()

def get_settings(request: Request) -> Settings:
    return request.app.state.settings

@router.get("/api/v1/tenants/{tenantId}/documents/search", response_model=SearchResponse)
def search(
    tenantId: str,
    q: str,
    limit: int = 10,
    offset: int = 0,
    request: Request = None,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    settings = get_settings(request)
    timer = MetricTimer(tenantId, "/api/v1/tenants/{tenantId}/documents/search", "GET")
    conn = connect(settings.db_path)
    try:
        actor = authorize_tenant(settings, tenantId, x_api_key)
        total, items = search_documents(conn, tenantId, q, limit, offset)
        audit(conn, tenantId, actor, "search", {"q": q, "limit": limit, "offset": offset, "returned": len(items)})
        timer.observe(status_code=200, is_error=False)
        return SearchResponse(
            query=q,
            limit=limit,
            offset=offset,
            total=total,
            results=[SearchResultItem(**i) for i in items],
        )
    except HTTPException as e:
        timer.observe(status_code=e.status_code, is_error=True)
        raise
    except Exception as e:
        timer.observe(status_code=500, is_error=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
