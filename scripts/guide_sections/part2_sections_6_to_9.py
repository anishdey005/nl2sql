"""
Part 2 of the Project Interview Guide:
Sections 6 to 9:
6. Technology Deep Dive (Python, FastAPI, SQLite, Groq, sqlglot, Chart.js, etc.)
7. Database Deep Dive (22 Relational Entities, Indexes, Storage Engines, Concurrency)
8. API & Backend Interview Preparation (REST, Status Codes, Security, Idempotency)
9. Scalability Engineering (10 to 1,000,000 users, Bottlenecks & Solutions)
"""

def get_content() -> str:
    return """# 6. Technology Deep Dive

Below is an exhaustive technical evaluation of every core technology in the NexSQL stack. For each technology, we analyze what it is, why it was chosen, how it is implemented, alternative choices, pros/cons, trade-offs, and critical interview defense questions.

---

### 1. Python 3.14 / 3.x
- **What it is**: High-level, dynamically typed, interpreted programming language with a rich ecosystem for data engineering and AI orchestration.
- **Why it was used**: Python is the lingua franca of AI/LLM engineering. The official Groq SDK (`groq`), AST parser (`sqlglot`), and ASGI frameworks (`fastapi`) offer first-class Python support.
- **How it is used**: Powers the entire backend: graph traversal (`catalog.py`), AST parsing (`validator.py`), API routing (`app.py`), and evaluation (`evaluator.py`).
- **Alternatives**: Go (Golang), TypeScript / Node.js, Rust.
- **Why choose alternatives**: Go offers compiled single-binary deployments and low memory footprint; Rust offers zero-cost abstractions and memory safety; Node.js aligns with full-stack TypeScript teams.
- **Advantages**: Rapid prototyping, expressive data structures (sets, dicts, tuples), and mature AI/data libraries.
- **Disadvantages**: Global Interpreter Lock (GIL) limits true multi-core CPU parallelism in a single process; higher memory footprint than compiled languages.
- **Interview Question**: *"Python is interpreted and historically slow. Why use it for a sub-second system?"*  
  **Strong Answer**: *"Because in an NL-to-SQL pipeline, the primary latency bottleneck is either LLM token generation (an external network I/O call) or database execution (handled by SQLite's optimized C engine). The application code itself—graph traversal, regex sanitization, and AST parsing—executes in under 5 milliseconds. Python’s rich ecosystem for LLMs and AST libraries like `sqlglot` far outweighs the marginal microsecond gains of a lower-level language."*

---

### 2. FastAPI
- **What it is**: Modern, high-performance web framework for building APIs with Python based on standard Python type hints, Starlette, and Pydantic.
- **Why it was used**: Built-in data validation via Pydantic, automatic OpenAPI/Swagger documentation generation, native asynchronous support, and minimal boilerplate.
- **How it is used**: Defines endpoints in `backend/app.py` (`/api/query`, `/api/schema`, etc.), parses JSON payloads, handles CORS, and serves static files.
- **Alternatives**: Flask, Django REST Framework (DRF), Express.js (Node.js), Gin (Go).
- **Why choose alternatives**: Flask is simpler for ultra-tiny microservices; Django provides a full-featured ORM and admin panel out-of-the-box.
- **Advantages**: High performance (one of the fastest Python frameworks), automatic JSON schema validation, native async/await syntax.
- **Disadvantages**: Relatively young compared to Django; requires an ASGI server like Uvicorn.
- **Interview Question**: *"How does FastAPI handle concurrency compared to Flask?"*  
  **Strong Answer**: *"Flask is traditionally a WSGI framework where synchronous routes block an entire worker thread unless running under greenlets or multiple processes. FastAPI is an ASGI framework built on Starlette and AnyIO. When declaring `async def` endpoints, it runs on an event loop. Even for synchronous `def` endpoints, FastAPI automatically offloads execution to an external threadpool, preventing blocking of the main event loop."*

---

### 3. SQLite 3
- **What it is**: Self-contained, serverless, zero-configuration, transactional SQL database engine running entirely in-process.
- **Why it was used**: Zero operational overhead; runs out-of-the-box on any machine without provisioning separate database servers or credentials. Allows deterministic seeding (`seed_data.py`).
- **How it is used**: Stores the 22 enterprise tables (`data/enterprise.db`). Queried via Python’s built-in `sqlite3` driver using read-only URI mode (`?mode=ro`).
- **Alternatives**: PostgreSQL, MySQL, DuckDB, MongoDB.
- **Why choose alternatives**: PostgreSQL provides enterprise-grade concurrency, row-level locking, and rich window functions; DuckDB is optimized for columnar OLAP queries over large Parquet files.
- **Advantages**: Single-file storage, no network latency between app and DB, ACID-compliant.
- **Disadvantages**: Coarse-grained concurrency (database-level locking on writes); lacks advanced user role permissioning.
- **Interview Question**: *"Why use SQLite for an enterprise project instead of PostgreSQL?"*  
  **Strong Answer**: *"For this implementation, SQLite allowed us to deliver a completely reproducible, zero-configuration local application where 2,460 rows across 22 normalized tables could be deterministically seeded and version-controlled. Furthermore, connecting via `?mode=ro` provides kernel-level read-only security. In our production architecture, we explicitly specify migrating to PostgreSQL with read replicas for high-concurrency enterprise workloads."*

---

### 4. Groq API & Llama 3.1 8B Instant
- **What it is**: Cloud inference provider utilizing custom Language Processing Units (LPUs) based on a Tensor Streaming Processor (TSP) architecture, running Meta's open-weights Llama 3.1 8B parameter model.
- **Why it was used**: Blazing inference speed. While traditional GPUs decode tokens at 30–80 tokens/sec, Groq LPUs achieve 500–800 tokens/sec, translating natural language into SQL in 200–400ms.
- **How it is used**: Invoked in `backend/core/engine.py` via `groq.Groq.chat.completions.create` with temperature 0.0 and max tokens 600.
- **Alternatives**: OpenAI API (GPT-4o), Anthropic (Claude 3.5 Sonnet), Self-hosted vLLM on NVIDIA GPUs.
- **Why choose alternatives**: Frontier models (GPT-4o, Sonnet) have higher reasoning capacity on multi-step logic; self-hosted vLLM guarantees data sovereignty within a private VPC.
- **Advantages**: Sub-second latency, deterministic outputs at temperature 0.0, low API cost compared to frontier models.
- **Disadvantages**: Smaller 8B parameter capacity requires careful prompt engineering and schema pruning to match larger models; external cloud dependency.
- **Interview Question**: *"What makes Groq so much faster than running on an NVIDIA H100?"*  
  **Strong Answer**: *"Traditional GPUs rely on High Bandwidth Memory (HBM) where memory bandwidth is the primary bottleneck during sequential token generation (decoding phase). Groq LPUs discard traditional caches and DRAM in favor of on-chip Static RAM (SRAM) interconnected with massive bandwidth (80 TB/s). Their architecture uses deterministic compiler scheduling rather than dynamic runtime scheduling, generating tokens sequentially without memory stall bottlenecks."*

---

### 5. sqlglot
- **What it is**: Pure Python SQL parser, transpiler, optimizer, and Abstract Syntax Tree (AST) engine supporting 20+ SQL dialects.
- **Why it was used**: Regex is notoriously inadequate for SQL validation because attackers can bypass regex with whitespace, comments, subqueries, or hex encodings. `sqlglot` parses queries into a syntactic tree.
- **How it is used**: In `backend/core/validator.py`, parses queries into ASTs (`sqlglot.parse`), checks for mutating expression nodes (`exp.Insert`, `exp.Delete`, `exp.Drop`), verifies table names, and programmatically rewrites ASTs to inject `LIMIT 200`.
- **Alternatives**: `sqlparse`, `pglast` (Postgres only), custom regex parsers.
- **Why choose alternatives**: `sqlparse` is lightweight but only provides lexical tokenization, not full AST expression trees; `pglast` provides libpg_query bindings but is Postgres-specific.
- **Advantages**: Dialect-aware (specifically understands SQLite syntax), rich AST node classes (`exp.Select`, `exp.Table`), supports AST mutations.
- **Disadvantages**: Parsing adds 1–3ms of CPU time per query; syntax errors in generated SQL must be handled gracefully.

---

### 6. Chart.js & Vanilla Frontend Stack
- **What it is**: HTML5 Canvas-based data visualization library paired with native HTML5, CSS3, and ES6 JavaScript.
- **Why it was used**: No complex build pipeline (Vite, Webpack, Babel, npm dependencies). Single static files served directly by FastAPI. Zero frontend build failures.
- **How it is used**: `frontend/app.js` inspects result column metadata. If 1 categorical and 1 numeric column are detected, dynamically creates Bar or Doughnut charts; if time-series dates are detected, renders Line charts.
- **Alternatives**: React, Vue, Svelte, Plotly.js, D3.js.
- **Why choose alternatives**: React/Next.js enables rich component ecosystems for multi-page SaaS applications; D3.js offers custom bespoke visualizations.
- **Advantages**: Instant page loads, zero client-side package bloat, clean separation of concerns.
- **Disadvantages**: Lacks virtual DOM diffing for extremely complex client-side state transitions.

---

# 7. Database Deep Dive: 22 Relational Entities & Indexing

## Complete 22-Table Schema Analysis

The database (`data/enterprise.db`) contains 22 normalized relational tables modeling an enterprise e-commerce, logistics, and CRM ecosystem.

```text
[ departments ] ──< [ employees ] ──< [ warehouses ] ──< [ inventory_items ] >── [ products ]
         │                  │                 │                                     │
         │                  v                 v                                     v
         │          [ support_tickets ]  [ shipments ]                      [ product_variants ]
         │                  │                 │                                     │
         │                  v                 │                                     v
         │          [ ticket_messages ]       │                             [ product_categories ]
         │                                    │                                     │
         v                                    v                                     v
[ audit_logs ]                          [ orders ] ──< [ order_items ] >──── [ purchase_orders ]
                                              │                                     │
                                              v                                     v
                                        [ payments ]                    [ purchase_order_items ]
                                              │                                     │
                                              v                                     v
                                        [ customers ] ────────────────────> [ suppliers ]
                                              │
                                              v
                                    [ customer_addresses ]
```

### Table Schema & Purpose Matrix
1. `departments` (8 rows): `department_id` (PK), `name` (UNIQUE), `code` (UNIQUE), `budget`, `created_at`. Models organizational divisions.
2. `employees` (25 rows): `employee_id` (PK), `department_id` (FK), `manager_id` (Self-FK), `first_name`, `last_name`, `email` (UNIQUE), `job_title`, `salary`, `hire_date`, `status`. Models staff hierarchy and payroll.
3. `customers` (100 rows): `customer_id` (PK), `first_name`, `last_name`, `email` (UNIQUE), `customer_segment` (CHECK: Enterprise, SMB, Consumer, VIP), `status`, `created_at`. Models customer base.
4. `customer_addresses` (120 rows): `address_id` (PK), `customer_id` (FK), `address_type`, `street`, `city`, `state`, `postal_code`, `country`, `is_default`. Models physical shipping/billing locations.
5. `product_categories` (10 rows): `category_id` (PK), `parent_category_id` (Self-FK), `name` (UNIQUE), `description`. Models category taxonomy.
6. `products` (50 rows): `product_id` (PK), `category_id` (FK), `name`, `sku` (UNIQUE), `description`, `base_price`, `cost_price`, `is_active`, `created_at`. Master catalog.
7. `product_variants` (100 rows): `variant_id` (PK), `product_id` (FK), `sku` (UNIQUE), `color`, `size`, `price_adjustment`, `stock_quantity`. SKU variations.
8. `suppliers` (15 rows): `supplier_id` (PK), `name`, `contact_name`, `email` (UNIQUE), `city`, `country`, `rating` (CHECK 1.0 to 5.0), `status`. Component suppliers.
9. `warehouses` (6 rows): `warehouse_id` (PK), `manager_employee_id` (FK), `name`, `location_city`, `state`, `capacity_units`. Logistics storage hubs.
10. `inventory_items` (150 rows): `inventory_id` (PK), `product_id` (FK), `variant_id` (FK), `warehouse_id` (FK), `quantity_on_hand`, `reorder_point`, `last_restocked_at`. Real-time stock.
11. `purchase_orders` (40 rows): `po_id` (PK), `supplier_id` (FK), `warehouse_id` (FK), `created_by_employee_id` (FK), `order_date`, `total_amount`, `status`. Supplier purchase orders.
12. `purchase_order_items` (120 rows): `po_item_id` (PK), `po_id` (FK), `product_id` (FK), `quantity_ordered`, `unit_cost`, `quantity_received`. PO line items.
13. `coupons` (15 rows): `coupon_id` (PK), `code` (UNIQUE), `discount_type`, `discount_value`, `min_order_amount`, `start_date`, `end_date`, `max_uses`, `times_used`, `is_active`. Marketing promos.
14. `orders` (200 rows): `order_id` (PK), `customer_id` (FK), `shipping_address_id` (FK), `order_date`, `status`, `subtotal`, `tax_amount`, `shipping_fee`, `discount_amount`, `total_amount`, `payment_method`. Orders.
15. `order_items` (461 rows): `order_item_id` (PK), `order_id` (FK), `product_id` (FK), `variant_id` (FK), `quantity`, `unit_price`, `total_price`. Order lines.
16. `payments` (200 rows): `payment_id` (PK), `order_id` (FK), `payment_date`, `amount`, `payment_method`, `payment_status`, `transaction_reference`. Transactions.
17. `shipments` (180 rows): `shipment_id` (PK), `order_id` (FK), `warehouse_id` (FK), `carrier` (FedEx, UPS, DHL, USPS), `tracking_number`, `ship_date`, `actual_delivery`, `shipment_status`. Deliveries.
18. `reviews` (150 rows): `review_id` (PK), `product_id` (FK), `customer_id` (FK), `rating` (CHECK 1-5), `title`, `comment`, `review_date`, `is_verified_purchase`. Ratings.
19. `discounts_applied` (80 rows): `discount_id` (PK), `order_id` (FK), `coupon_id` (FK), `amount_saved`, `applied_at`. Coupon redemptions.
20. `support_tickets` (80 rows): `ticket_id` (PK), `customer_id` (FK), `assigned_employee_id` (FK), `subject`, `priority`, `status`, `category`, `created_at`, `resolved_at`. Helpdesk issues.
21. `ticket_messages` (200 rows): `message_id` (PK), `ticket_id` (FK), `sender_type`, `sender_id`, `message_text`, `created_at`. Ticket chat history.
22. `audit_logs` (150 rows): `log_id` (PK), `entity_name`, `entity_id`, `action`, `changed_by_employee_id` (FK), `timestamp`, `details`. Audit compliance log.

---

### Database Indexing Strategy
In `backend/db/schema.sql`, 12 performance B-Tree indexes were created on high-frequency join foreign keys:
```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_items (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory_items (warehouse_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews (product_id);
CREATE INDEX IF NOT EXISTS idx_tickets_customer ON support_tickets (customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON support_tickets (assigned_employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees (department_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id);
```
- **Why it matters**: Without these indexes, joining `orders` with `order_items` would require full table scans ($O(N \\times M)$ complexity). With B-Tree indexes, lookups drop to $O(N \\log M)$ logarithmic index seeks.

---

### Critical Database Interview Defense Q&A

#### Q: "Why SQL and relational modeling instead of NoSQL like MongoDB?"
**Strong Answer**:
> *"The domain modeled here is fundamentally relational with strict relational constraints: customers place orders, orders contain line items of products, products belong to categories and have inventory in warehouses.
> 
> If we chose MongoDB, we would face a classic dilemma: either embed documents (e.g. embedding order items inside orders, which duplicates product and pricing data and creates write anomalies when product details update), or reference documents via ObjectIds, which requires multiple `$lookup` pipeline stages that essentially mimic relational joins with higher compute overhead and weaker schema guarantees.
> 
> Furthermore, natural language queries frequently ask for cross-cutting aggregations across multiple domains (e.g., 'Compare customer reviews with return rates and supplier ratings'). Relational SQL handles multi-table joins natively with declarative optimization, indexing, and strict ACID guarantees."*

#### Q: "What happens when the database grows from 2,400 rows to 100 million rows?"
**Strong Answer**:
> *"1. **Table Partitioning**: Range-partition high-volume tables like `orders`, `order_items`, and `audit_logs` by date (e.g. monthly partitions). Queries filtering on `order_date >= '2024-01-01'` immediately prune 90% of data blocks.  
> 2. **Read/Write Splitting**: Migrate from SQLite to PostgreSQL with an active primary for transactions and multiple asynchronous streaming read replicas for analytical queries.  
> 3. **Materialized Views & Summary Tables**: Pre-aggregate daily and monthly sales metrics (`daily_revenue_by_category`) refreshed asynchronously, so executive dashboards avoid scanning 100 million raw line items.  
> 4. **Hot vs Cold Storage**: Archive historical orders older than 3 years to object storage (S3) queryable via AWS Athena or DuckDB."*

#### Q: "What happens if two users execute queries simultaneously in your current setup?"
**Strong Answer**:
> *"Because all application queries are strictly read-only SELECT statements opened via SQLite URI mode `?mode=ro`, multiple reader threads can execute concurrently without blocking. SQLite allows concurrent shared locks for readers. However, if a write process (such as a seed or ingestion job) attempts to write, SQLite locks the entire database file with an exclusive lock, causing concurrent readers to wait or time out. In production, PostgreSQL handles this via Multi-Version Concurrency Control (MVCC), where readers never block writers and writers never block readers."*

---

# 8. API & Backend Interview Preparation

## Complete REST API Specification

### 1. `POST /api/query`
- **Purpose**: Core translation endpoint. Translates natural language into SQL, validates, heals errors, executes, and returns data and visualization recommendations.
- **Request Body** (`QueryRequest`):
  ```json
  {
    "prompt": "Show top 5 customers by spend",
    "api_key": "gsk_...",        // Optional, defaults to env GROQ_API_KEY
    "model": "llama-3.1-8b-instant", // Optional
    "max_rows": 200              // Optional default 200
  }
  ```
- **Validation**: Rejects empty prompts with HTTP 400 Bad Request.
- **Response Body**:
  ```json
  {
    "success": true,
    "sql": "SELECT c.customer_id, ... LIMIT 5",
    "error": null,
    "columns": ["customer_id", "first_name", "total_spent"],
    "rows": [{"customer_id": 2, "first_name": "Riley", "total_spent": 12450.50}],
    "row_count": 5,
    "tables_used": ["customers", "orders"],
    "mode": "groq_llama_3.1_8b",
    "model": "llama-3.1-8b-instant",
    "correction_attempts": 0,
    "explanation": "Aggregates and summarizes records...",
    "visualization": {"type": "bar", "x_axis": "first_name", "y_axis": "total_spent", "title": "..."},
    "timing": {"llm_ms": 284.1, "exec_ms": 4.2, "total_ms": 288.3, "is_sub_second": true}
  }
  ```
- **Status Codes**: 200 OK (successful execution or handled validation failure), 400 Bad Request (empty prompt), 500 Internal Server Error (unhandled system failure).

### 2. `GET /api/schema`
- **Purpose**: Returns metadata for all 22 tables, column types, PK/FK flags, and 29 foreign-key relationships.
- **Response Body**:
  ```json
  {
    "total_tables": 22,
    "total_records": 2460,
    "tables": [
      {
        "name": "customers",
        "description": "Customers who purchase products...",
        "row_count": 100,
        "columns": [{"name": "customer_id", "type": "INTEGER PRIMARY KEY", "is_primary_key": true, ...}],
        "keywords": ["customer", "client", "buyer"]
      }
    ],
    "relationships": [
      {"source": "customers", "target": "orders", "on_clause": "customers.customer_id = orders.customer_id"}
    ]
  }
  ```

### 3. `GET /api/sample-queries`
- **Purpose**: Returns curated business prompts categorized by domain (Executive & Sales, Supply Chain & Logistics, Customer & Support, HR & Org).

### 4. `POST /api/benchmark/run`
- **Purpose**: Runs automated evaluation across test queries (limit: 15 to 105).
- **Request Body**: `{"limit": 15, "api_key": "gsk_...", "category": null, "difficulty": null}`
- **Response Body**: Returns overall metrics (validity rate %, execution accuracy %, avg latency ms) and detailed query-by-query breakdown.

### 5. `GET /api/benchmark/latest`
- **Purpose**: Fast retrieval of cached `benchmark_report.json` without re-running all queries.

### 6. `POST /api/verify-key`
- **Purpose**: Tests a user-provided Groq API key via a lightweight test completion.
- **Request Body**: `{"api_key": "gsk_test123"}`
- **Response**: `{"valid": true, "message": "Groq API key verified successfully!"}`

---

## Backend Concepts Interview Defense

### REST Architecture & Methods
- **GET vs POST**: GET must be safe and idempotent (no state change, cacheable). In our project, `/api/schema` and `/api/sample-queries` are GET because they only read data. `/api/query` is POST even though it executes a database `SELECT` because the payload contains complex natural language prompts, arbitrary length text, and potentially user API keys that should never be logged in URL query parameters or web server access logs.
- **PUT vs PATCH**: PUT replaces the target resource entirely; PATCH applies a partial update. (Currently, neither is used in NexSQL because the system is strictly read-only).
- **Idempotency**: An operation is idempotent if applying it multiple times produces the exact same server state as applying it once. GET, PUT, DELETE are idempotent. POST is typically non-idempotent.

### Cross-Origin Resource Sharing (CORS)
- **Current Implementation**: `CORSMiddleware` is configured in `backend/app.py` allowing `allow_origins=["*"]`.
- **Interview Critique**: *"In development, wildcard `*` CORS is acceptable. In production, this is a security risk. Production configuration must restrict origins to trusted internal corporate domains (e.g., `allow_origins=["https://analytics.enterprise.com"]`) and forbid credentials on wildcard origins."*

---

# 9. Scalability Engineering: From 10 to 1,000,000 Users

| Concurrency Tier | System Behavior Today (`CURRENT IMPLEMENTATION`) | Bottlenecks Encountered | Architectural Solution (`RECOMMENDED IMPROVEMENT`) |
| :---: | :--- | :--- | :--- |
| **10 Users** | Works flawlessly. SQLite executes in ~4ms, Groq responds in ~300ms. CPU usage <5%. | None. Single Uvicorn process handles 10 concurrent connections easily. | Current single-node setup is sufficient. |
| **1,000 Users** | Latency degrades. Groq API rate limits (tokens per minute) will throttle requests. SQLite read lock contention starts under high concurrency. | 1. Groq API Rate Limits (429 Too Many Requests)<br>2. OS File Descriptor Limits<br>3. Uvicorn Worker Saturation | 1. Introduce Redis semantic cache for popular queries<br>2. Deploy 2–4 Uvicorn worker processes behind NGINX<br>3. Connection pooling |
| **100,000 Users** | Complete system failure. Single SQLite database crashes from file I/O locks. Single server CPU saturates. Groq costs explode. | 1. Database File I/O & Locks<br>2. Single-Node Memory/CPU Exhaustion<br>3. Network egress saturation | 1. Migrate to PostgreSQL with 3 Read Replicas<br>2. Horizontal scaling (Kubernetes cluster with 10–20 pods)<br>3. Redis Cluster for query & metadata caching |
| **1,000,000 Users** | Requires distributed multi-region architecture. | 1. Global network latency<br>2. Database connection pool exhaustion<br>3. Massive write & analytics contention | 1. Multi-region AWS deployment with Cloudflare edge routing<br>2. Kafka message bus for asynchronous heavy query processing<br>3. Read replicas + distributed data warehouse (ClickHouse / Snowflake) |

### Detailed Bottleneck Progression Analysis
1. **The First Bottleneck: External LLM Rate Limits & Latency**:
   - Calling Groq Cloud API for every single query means you are constrained by their API tier (e.g., 6,000 requests per minute). If 1,000 users ask queries simultaneously, you hit HTTP 429 errors.
   - *Fix*: Cache query embeddings in Redis. If the cosine similarity between a new prompt and a cached prompt is $>0.95$, serve the cached SQL immediately (reducing external calls by 40–60%).
2. **The Second Bottleneck: SQLite Single-File Storage**:
   - SQLite operates on a local file descriptor. Under hundreds of concurrent readers, operating system disk I/O and shared file locks introduce thread latency.
   - *Fix*: Migrate to PostgreSQL Amazon RDS with connection pooling via PgBouncer.
3. **The Third Bottleneck: Synchronous Request/Response Cycle**:
   - If a user requests a complex join over millions of rows with CSV export, keeping an open HTTP socket for 15 seconds exhausts web server connection slots.
   - *Fix*: Decouple heavy queries using an asynchronous worker queue (Celery + RabbitMQ). The API returns a `task_id` with HTTP 202 Accepted, and the frontend polls or listens via WebSockets.
"""
