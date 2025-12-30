import os
import random
import time
import requests

BASE = os.getenv("BASE_URL", "http://localhost:8000")
TENANT = os.getenv("TENANT", "tenantA")
KEY = os.getenv("API_KEY", "keyA")

WORDS = ["knowledge","customer","support","agent","workflow","search","index","compliance","audit","tenant","egain","case","resolution","bot","assistant"]

def rand_text(n_words=120):
    return " ".join(random.choice(WORDS) for _ in range(n_words))

def ingest(n=5000):
    for i in range(n):
        r = requests.post(
            f"{BASE}/api/v1/tenants/{TENANT}/documents",
            headers={"X-API-Key": KEY},
            json={"title": f"doc-{i}", "content": rand_text(), "tags": ["bench"]},
            timeout=10,
        )
        r.raise_for_status()
    print(f"Ingested {n} docs")

def search(q="knowledge", reps=200):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        r = requests.get(
            f"{BASE}/api/v1/tenants/{TENANT}/documents/search",
            headers={"X-API-Key": KEY},
            params={"q": q, "limit": 10, "offset": 0},
            timeout=10,
        )
        r.raise_for_status()
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    p50 = times[len(times)//2]
    p95 = times[int(len(times)*0.95)-1]
    print(f"search reps={reps} p50={p50:.2f}ms p95={p95:.2f}ms")

if __name__ == "__main__":
    # Uncomment to populate local DB:
    # ingest(10000)
    search()
