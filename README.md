# eGain Platform Engineering Assignment – Vinod Dhomse

This repository contains my submission for the **eGain Platform Engineering take-home assignment**.  
It includes the system design, core implementation, and infrastructure-as-code components described in the problem statement.

The solution is intentionally structured so reviewers can understand the design and tradeoffs
by reading documentation alone, without needing to run the services.

---

## Repository Structure (Read This First)

```text
.
├── README.md                     # Submission overview (this file)
├── DESIGN.md                     # System design (Markdown)
├── design/
│   └── egain_system_design.pdf   # System design (PDF)
├── app/                          # Part 2: Core implementation source code (FastAPI)
│   ├── README.md                 # Implementation details, API usage, examples
│   └── *.py                             
├── tests/                        # Unit tests
├── scripts/
│   └── benchmark.py              # Basic performance benchmark
├── iac/
│   └── terraform/                # Part 3: Infrastructure as Code
│       ├── README.md             # IaC instructions and explanations
│       └── *.tf
```
---

## Part 1 – System Design

The system design describes a **multi-tenant knowledge indexing and search platform**, including:

- High-level architecture and data flow
- Tenant isolation strategy
- Scalability and performance considerations
- Security and compliance approach
- Technology choices and tradeoffs

**Design documents:**
- PDF: [design/egain_system_design.pdf](design/egain_system_design.pdf)
- Architecture Diagram (Mermaid): [design/architecture_diagram.md](design/architecture_diagram.md)

---

## Part 2 – Core Implementation

The core implementation is a **simplified, local-first version** of the platform using:

- Python + FastAPI
- SQLite with SQLite FTS5 for full-text search
- API-key-based tenant authentication
- Health and metrics endpoints
- Unit tests and basic performance benchmarking

**Key features implemented:**
- Tenant-isolated document ingestion
- Full-text search with ranking (BM25)
- Pagination support
- Per-tenant metrics and health checks

**Detailed setup instructions, API documentation, and examples** are provided in:

👉 **[app/README.md](app/README.md)**

This includes:
- Environment setup
- How to run the service
- Swagger/OpenAPI documentation
- Example curl commands
- How to run tests and benchmarks

---

## Part 3 – Infrastructure as Code

Infrastructure as Code (IaC) is provided using **Terraform on AWS**, modeling how this service
would be deployed in a production environment.

The Terraform configuration includes:
- ECS Fargate for container orchestration
- Application Load Balancer (ALB)
- API Gateway (HTTP API)
- RDS MySQL (production data store mapping)
- CloudWatch logs and alarms
- IAM roles and policies
- Blue-green deployments using ECS + CodeDeploy
- Autoscaling based on CPU and memory utilization

**IaC documentation and deployment instructions:**
👉 **`iac/terraform/README.md`**

---

## Setup Instructions

See **[app/README.md](app/README.md)** for:
- Local setup
- Environment variables
- Running the service

---

## Running Tests

See **[app/README.md](app/README.md)** for instructions to run unit tests and benchmarks.

---

## API Usage Examples

Detailed API usage examples (ingestion, search, metrics) are documented in:

👉 **[app/README.md](app/README.md)**

Swagger UI is available when running locally at:
http://localhost:8000/docs


---

## Time Spent

- Part 1 (System design): ~X hours
- Part 2 (Core implementation, tests, benchmarking): ~Y hours
- Part 3 (Infrastructure as Code): ~Z hours
- Documentation, cleanup, and packaging: ~W hours

---

## Assumptions

- The assignment implementation accepts **extracted text content** rather than raw files
  (PDF/DOCX). File parsing and normalization would be handled by a separate ingestion layer.
- SQLite and SQLite FTS5 are used to demonstrate embedded storage and indexing for local execution;
  production deployments would use RDS and OpenSearch.
- API-key-based authentication is sufficient for the assignment; production systems would use OAuth/OIDC.

---

## What I Would Do Differently With More Time

- Add a durable ingestion pipeline using Amazon SQS with DLQ support
- Support file uploads (PDF/DOCX) with a parser/normalizer layer
- Integrate OpenSearch for distributed indexing and hybrid ranking
- Add OAuth/OIDC authentication and fine-grained RBAC
- Add per-tenant rate limiting and quotas at API Gateway
- Improve observability with Prometheus-style metrics and dashboards
- Expand load testing and failure/chaos testing

---

## Notes for Reviewers

This repository is structured to allow evaluation through documentation alone.
If you choose to run the service locally, all required steps are documented in [app/README.md](app/README.md).
