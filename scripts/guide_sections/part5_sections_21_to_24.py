"""
Part 5 of the Project Interview Guide:
Sections 21 to 24:
21. Cloud Deployment Strategy (AWS / Cloudflare Blueprint)
22. Observability: Metrics, Logs & Tracing (4 Golden Signals)
23. Testing Strategy & Code Quality (Existing vs Missing Tests)
24. Design Patterns & Software Engineering Principles in Code
"""

def get_content() -> str:
    return """# 21. Cloud Deployment Strategy

Below is a battle-tested cloud deployment architecture designed for AWS and Cloudflare.

```text
[ Cloudflare (Edge CDN / DNS / WAF) ]
                 │ (HTTPS / TLS 1.3)
                 ▼
[ AWS Internet Gateway ──► Application Load Balancer (Public Subnet) ]
                                 │
     +---------------------------+---------------------------+
     │ (Private VPC Subnet 1)                                │ (Private VPC Subnet 2)
     v                                                       v
[ AWS ECS Fargate: Pod 1 ]                              [ AWS ECS Fargate: Pod 2 ]
(FastAPI Application Container)                         (FastAPI Application Container)
     │                                                       │
     +---------------------------+---------------------------+
                                 │
                 +---------------+---------------+
                 │                               │
                 v                               v
[ AWS ElastiCache for Redis ]         [ Amazon RDS PostgreSQL 16 ]
(VPC Private Subnet)                  (Multi-AZ Deployment + Read Replica)
```

### Why This Specific Cloud Blueprint?
1. **AWS ECS Fargate (Serverless Containers)**:
   - Eliminates the operational overhead of managing EC2 Linux AMIs, OS patches, or complex Kubernetes control planes.
   - You provide the Docker container image, specify CPU (1 vCPU) and RAM (2 GB), and AWS manages execution with auto-scaling.
2. **Amazon RDS PostgreSQL (Multi-AZ)**:
   - Provides automated backups, point-in-time recovery (PITR), synchronous standby failover in a secondary availability zone, and automated read replica replication.
3. **AWS ElastiCache for Redis**:
   - Fully managed in-memory caching cluster inside private VPC subnets with automated node failover and encryption at rest.

---

# 22. Observability: Metrics, Logs & Tracing

Observability is understanding the internal state of a system based on its external outputs. In production, we monitor the **Four Golden Signals** (Google SRE standard):

### The 4 Golden Signals for NexSQL
1. **Latency**:
   - Time spent in translation pipeline (P50, P90, P99).
   - *Target*: P50 < 350ms, P99 < 1.2s.
2. **Traffic**:
   - Query request rate (Requests Per Second - RPS).
3. **Errors**:
   - Rate of HTTP 4xx (validation/prompt errors) and HTTP 5xx (Groq API failures or unhandled database exceptions).
   - *Target*: Error rate < 0.5%.
4. **Saturation**:
   - Memory usage of Python containers, CPU utilization, database connection pool saturation, and Groq rate-limit quota consumption.

---

### Implementation Architecture (`RECOMMENDED IMPROVEMENT`)
- **Structured JSON Logging**: Replace Python `print()` statements with structured JSON logging (`structlog`):
  ```json
  {"timestamp": "2026-10-06T12:00:00Z", "level": "INFO", "event": "query_executed", "query_hash": "a1b2", "latency_ms": 284.1, "row_count": 5, "tables": ["customers", "orders"]}
  ```
- **Prometheus & Grafana**:
  - Expose a `/metrics` endpoint via `prometheus-fastapi-instrumentator`.
  - Prometheus scrapes every 15s; Grafana visualizes latency percentiles and accuracy metrics.
- **Distributed Tracing (OpenTelemetry)**:
  - Propagates a `trace_id` through API gateway -> FastAPI route -> Groq SDK -> SQLite execution. Pinpoints whether latency spikes originate in model inference or database disk I/O.

---

# 23. Testing Strategy & Code Quality

## Analysis of Existing Tests (`CURRENT IMPLEMENTATION`)
The test file `tests/test_engine.py` contains 13 automated tests organized into 4 test classes:
1. `TestDatabaseAndCatalog`:
   - `test_database_exists_and_connected`: Verifies `data/enterprise.db` exists and contains at least 22 tables.
   - `test_table_row_counts_exceed_1000_records`: Asserts total row count >= 1,000 (actual: 2,460 rows) and verifies zero empty tables.
   - `test_schema_join_paths`: Tests BFS graph pathfinding between `customers` and `products`.
2. `TestSQLValidatorSecurity`:
   - `test_blocks_drop_table`: Verifies `DROP TABLE customers;` is rejected.
   - `test_blocks_delete`: Verifies `DELETE FROM orders` is blocked.
   - `test_blocks_update`: Verifies `UPDATE products` is blocked.
   - `test_blocks_insert`: Verifies `INSERT INTO departments` is blocked.
   - `test_blocks_unknown_table`: Verifies unwhitelisted table queries are rejected.
   - `test_enforces_limit_on_unbounded_query`: Verifies `LIMIT 200` injection.
3. `TestNL2SQLEngine`:
   - `test_process_query_top_customers`: Validates end-to-end execution, rows returned, and sub-second timing.
   - `test_process_query_low_stock`: Tests multi-table inventory join query.
   - `test_process_query_monthly_revenue`: Tests date aggregation and visualization recommendation.
4. `TestBenchmarkEvaluation`:
   - `test_benchmark_runner_metrics`: Runs 20 test cases and asserts validity >= 95%, accuracy >= 75%, and latency < 1,000ms.

---

## Missing Tests & Prioritized Testing Strategy (`RECOMMENDED IMPROVEMENT`)

| Priority | Test Category | Specific Test Case Needed | Why It Matters |
| :---: | :--- | :--- | :--- |
| **P0** | **SQL Injection Fuzzing** | Stacked queries with comment evasion (`SELECT 1; -- DROP TABLE customers;`), SQL dialect hex-encoding | Verifies AST parser cannot be fooled by malicious edge cases. |
| **P0** | **Network Timeout Mocking** | Mock Groq SDK throwing `httpx.ConnectTimeout` and `httpx.HTTPStatusError(429)` | Confirms graceful fallback works deterministically during cloud outages. |
| **P1** | **Concurrency & Race Conditions**| Run 50 concurrent `process_query()` calls using `pytest-xdist` or `ThreadPoolExecutor` | Verifies SQLite thread safety under parallel reader connections. |
| **P1** | **Empty Result Edge Cases** | Natural language queries with valid SQL that return 0 rows | Confirms frontend table and chart renderers handle empty states without crashing. |
| **P2** | **Property-Based Testing** | Use `Hypothesis` to generate random strings as query prompts | Ensures the parser and validator never raise uncaught exceptions on malformed input. |

---

# 24. Design Patterns & Software Engineering Principles in Code

Unlike projects that claim design patterns exist when they do not, below are the patterns **that actually exist in the code right now**:

---

### 1. The Strategy Pattern (Offline vs Groq Translation)
- **Where**: `backend/core/engine.py` in `NL2SQLEngine.process_query()`
- **How it works**: The engine dynamically selects its translation strategy at runtime:
  - If a Groq API key is present: invokes the `generate_sql_groq` strategy.
  - If no key is present or Groq encounters a network error: invokes the `fallback_translate` heuristic strategy.
  - The client code (`backend/app.py`) interacts with the unified interface without needing to know which strategy executed.

---

### 2. The Facade Pattern (`NL2SQLEngine`)
- **Where**: `backend/core/engine.py`
- **How it works**: The client (`backend/app.py`) calls a single simple method: `engine.process_query(prompt)`.
- Behind this single call, the facade coordinates four complex subsystems:
  1. `SchemaCatalog`: keyword extraction and BFS graph traversal.
  2. `Groq SDK`: prompt synthesis and token generation.
  3. `SQLValidator`: AST validation, security checks, and row limits.
  4. Database execution, explanation generation, and chart recommendation.

---

### 3. Graph Adjacency List & BFS Algorithm (Shortest Join Path)
- **Where**: `backend/core/catalog.py`
- **How it works**: In `_build_graph()`, foreign keys are modeled as an undirected graph. In `find_shortest_join_path(start, end)`, a standard Breadth-First Search (BFS) queue traverses neighbors to compute the minimum number of table joins needed to connect any two tables.

---

### 4. Pipeline / Chain of Responsibility Pattern
- **Where**: `backend/core/validator.py`
- **How it works**: Incoming SQL passes sequentially through a pipeline of validation filters:
```text
Sanitize Text -> Keyword Check -> AST Parsing -> Statement Count Check -> AST Node Safety -> Table Whitelist -> Limit Injection
```
  If any step fails, the pipeline short-circuits and returns an informative error.

---

### 5. SOLID Principles Evaluation in the Codebase
- **Single Responsibility Principle (SRP)**:
  - `catalog.py` is solely responsible for schema metadata and join paths.
  - `validator.py` is solely responsible for security checks and database execution.
  - `engine.py` is responsible for LLM coordination.
- **Open/Closed Principle (OCP)**:
  - To add a 23rd table to the database, you only add its metadata dictionary in `TABLE_METADATA` and edges in `FOREIGN_KEY_EDGES`. The BFS pathfinder, prompt builder, and AST validator adapt automatically without modifying their algorithmic code.
"""
