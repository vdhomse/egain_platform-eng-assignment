import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Tuple

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ingest_document(conn: sqlite3.Connection, tenant_id: str, title: str, content: str, tags: List[str]) -> str:
    doc_id = str(uuid.uuid4())
    ts = utc_now_iso()
    tags_json = json.dumps(tags)

    conn.execute(
        "INSERT INTO documents (tenant_id, document_id, title, content, tags_json, created_at) VALUES (?,?,?,?,?,?)",
        (tenant_id, doc_id, title, content, tags_json, ts),
    )
    conn.execute(
        "INSERT INTO documents_fts (tenant_id, document_id, title, content) VALUES (?,?,?,?)",
        (tenant_id, doc_id, title, content),
    )
    conn.commit()
    return doc_id

def search_documents(conn: sqlite3.Connection, tenant_id: str, query: str, limit: int, offset: int) -> Tuple[int, list]:
    count_row = conn.execute(
        "SELECT COUNT(*) AS c FROM documents_fts WHERE tenant_id = ? AND documents_fts MATCH ?",
        (tenant_id, query),
    ).fetchone()
    total = int(count_row["c"]) if count_row else 0

    rows = conn.execute(
        '''
        SELECT document_id, title, content,
               bm25(documents_fts) AS bm25_score
        FROM documents_fts
        WHERE tenant_id = ? AND documents_fts MATCH ?
        ORDER BY bm25_score ASC
        LIMIT ? OFFSET ?
        ''',
        (tenant_id, query, limit, offset),
    ).fetchall()

    results = []
    for r in rows:
        content = r["content"]
        snippet = content[:200] + ("..." if len(content) > 200 else "")
        bm25_score = float(r["bm25_score"]) if r["bm25_score"] is not None else 0.0
        relevance = 1.0 / (1.0 + max(0.0, bm25_score))
        results.append({
            "document_id": r["document_id"],
            "title": r["title"],
            "snippet": snippet,
            "relevance_score": relevance,
        })
    return total, results

def audit(conn: sqlite3.Connection, tenant_id: str, actor: str, action: str, details: dict) -> None:
    conn.execute(
        "INSERT INTO audit_log (ts, tenant_id, actor, action, details_json) VALUES (?,?,?,?,?)",
        (utc_now_iso(), tenant_id, actor, action, json.dumps(details)),
    )
    conn.commit()

def document_count_per_tenant(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT tenant_id, COUNT(*) AS c FROM documents GROUP BY tenant_id").fetchall()
    return {r["tenant_id"]: int(r["c"]) for r in rows}
