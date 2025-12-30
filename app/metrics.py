import time
from dataclasses import dataclass
from typing import Dict
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

@dataclass
class TenantMetrics:
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0

    def record(self, latency_ms: float, is_error: bool) -> None:
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.total_latency_ms += latency_ms

    @property
    def avg_latency_ms(self) -> float:
        return 0.0 if self.request_count == 0 else self.total_latency_ms / self.request_count

    @property
    def error_rate(self) -> float:
        return 0.0 if self.request_count == 0 else self.error_count / self.request_count

TENANT_METRICS: Dict[str, TenantMetrics] = {}

REQ_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["tenant", "path", "method", "status"])
LAT_HIST = Histogram("http_request_latency_ms", "HTTP request latency in ms", ["tenant", "path", "method"])

def get_tenant_metrics(tenant_id: str) -> TenantMetrics:
    if tenant_id not in TENANT_METRICS:
        TENANT_METRICS[tenant_id] = TenantMetrics()
    return TENANT_METRICS[tenant_id]

class MetricTimer:
    def __init__(self, tenant: str, path: str, method: str):
        self.tenant = tenant
        self.path = path
        self.method = method
        self.start = time.perf_counter()

    def observe(self, status_code: int, is_error: bool) -> None:
        elapsed_ms = (time.perf_counter() - self.start) * 1000.0
        get_tenant_metrics(self.tenant).record(elapsed_ms, is_error)
        REQ_COUNTER.labels(self.tenant, self.path, self.method, str(status_code)).inc()
        LAT_HIST.labels(self.tenant, self.path, self.method).observe(elapsed_ms)

def prometheus_payload() -> bytes:
    return generate_latest()

CONTENT_TYPE = CONTENT_TYPE_LATEST
