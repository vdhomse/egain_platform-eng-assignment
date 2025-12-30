from fastapi import FastAPI
from fastapi.responses import Response
from .config import load_settings
from .logging_setup import setup_logging
from .db import connect, init_db
from .routers.ingestion import router as ingestion_router
from .routers.search import router as search_router
from .metrics import TENANT_METRICS, prometheus_payload, CONTENT_TYPE
from .services import document_count_per_tenant

def create_app() -> FastAPI:
    setup_logging()
    settings = load_settings()

    app = FastAPI(
        title="eGain Knowledge Indexing Service",
        version="0.1.0",
        description="Assignment implementation: multi-tenant ingestion + search + health + metrics",
    )
    app.state.settings = settings

    conn = connect(settings.db_path)
    init_db(conn)
    conn.close()

    app.include_router(ingestion_router)
    app.include_router(search_router)

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok", "db": settings.db_path}

    @app.get("/api/v1/metrics")
    def metrics():
        req = {t: m.request_count for t, m in TENANT_METRICS.items()}
        avg = {t: round(m.avg_latency_ms, 3) for t, m in TENANT_METRICS.items()}
        err = {t: round(m.error_rate, 6) for t, m in TENANT_METRICS.items()}

        conn = connect(settings.db_path)
        try:
            doc_counts = document_count_per_tenant(conn)
        finally:
            conn.close()

        return {
            "request_count_per_tenant": req,
            "avg_response_time_ms_per_tenant": avg,
            "document_count_per_tenant": doc_counts,
            "error_rate_per_tenant": err,
        }

    @app.get("/api/v1/metrics/prometheus")
    def prom_metrics():
        payload = prometheus_payload()
        return Response(content=payload, media_type=CONTENT_TYPE)

    return app

app = create_app()
