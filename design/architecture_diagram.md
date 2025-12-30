```mermaid
flowchart LR
  subgraph Clients["Clients"]
    UI["Admin UI / Tenant Tools"]
    Apps["Customer Apps / Integrations"]
  end

  Clients --> API["API Gateway / Load Balancer"]

  subgraph ControlPlane["Control Plane"]
    Auth["Auth & Tenant Management Service"]
    Config["Tenant Config Store"]
  end

  subgraph Ingest["Ingestion & Indexing"]
    IngestAPI["Ingestion Service"]
    MQ[("Ingestion Queue")]
    DLQ[("Dead Letter Queue")]
    Parser["Document Parser & Normalizer"]
    IndexWorker["Indexing Worker (Text + Embeddings)"]
  end

  subgraph Search["Search & Query"]
    SearchAPI["Search Service"]
  end

  subgraph Storage["Storage Layer"]
    ObjStore[("Object Storage - S3")]
    MetaDB[("Metadata DB")]
    SearchIndex[("Search / Vector Index Cluster")]
    AuditStore[("Audit Log Store")]
    Cache[("Redis Cache")]
  end

  subgraph DataPlane["Data Plane"]
    Ingest
    Search
    Storage
  end

  API --> Auth
  API --> IngestAPI
  API --> SearchAPI

  Auth --> MetaDB

  IngestAPI --> MQ
  MQ --> Parser
  MQ --> DLQ

  Parser --> ObjStore
  Parser --> MetaDB
  Parser --> IndexWorker

  IndexWorker --> SearchIndex

  SearchAPI --> Cache
  SearchAPI --> SearchIndex
  SearchAPI --> MetaDB

  API --> AuditStore
  IngestAPI --> AuditStore
  SearchAPI --> AuditStore
  IndexWorker --> AuditStore
