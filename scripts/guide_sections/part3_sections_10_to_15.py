"""
Part 3 of the Project Interview Guide:
Sections 10 to 15:
10. Redis: Caching, Locking, and Rate Limiting
11. RabbitMQ: Message Queuing & Task Decoupling
12. Kafka: Event Streaming & Kafka vs RabbitMQ Analysis
13. Synchronous vs Asynchronous Processing & Concurrency
14. Load Balancing & High Availability
15. CI/CD & DevOps Engineering
"""

def get_content() -> str:
    return """# 10. Redis: Caching, Locking, and Rate Limiting

> 🟢 **CURRENT IMPLEMENTATION**: Redis is **not currently used** in the codebase. All queries hit `SchemaCatalog` and `data/enterprise.db` directly in-process.  
> 🟡 **RECOMMENDED IMPROVEMENT**: Redis should be integrated as a distributed cache, token-bucket rate limiter, and query result store.

---

### What is Redis & Why Is It Fast?
Redis (Remote Dictionary Server) is an open-source, in-memory key-value data structure store used as a database, cache, and message broker.
- **Why it is fast**:
  1. **In-Memory Storage**: Data resides in RAM. RAM access times are measured in nanoseconds (~100ns), compared to Solid State Drives (SSDs) which take microseconds (~50–100µs) or spinning disks (~10ms).
  2. **Single-Threaded Event Loop (Core Engine)**: Redis uses an asynchronous, non-blocking I/O multiplexing event loop (epoll / kqueue). By processing commands sequentially in memory, Redis avoids the massive CPU overhead of thread context switching, lock contention, and race conditions.
  3. **Optimized C Data Structures**: Strings, Hashes, Lists, Sets, Sorted Sets (SkipLists), and HyperLogLogs are hand-tuned for minimal memory overhead and $O(1)$ or $O(\\log N)$ operations.

---

### Core Redis Architectural Patterns
1. **Cache-Aside Pattern (Lazy Loading)**:
   - Application receives a query.
   - Application checks Redis: `GET query:<hash>`.
   - **Cache Hit**: Returns cached SQL and results immediately (latency: 1–2ms).
   - **Cache Miss**: Application calls Groq Llama 3.1 8B, validates AST, executes on SQLite, and writes result to Redis with a TTL: `SETEX query:<hash> 3600 <result_json>`.
2. **Time-To-Live (TTL) & Cache Invalidation**:
   - Every cached item must have an explicit TTL (e.g. 1 hour).
   - *Write-Through Invalidation*: When new orders or inventory records are ingested, trigger a cache purge for affected keys.
3. **Cache Stampede (Thundering Herd) & Prevention**:
   - If a popular key expires and 500 concurrent users request it simultaneously, all 500 requests bypass the cache and hammer the LLM and database.
   - *Fix*: **Mutex Lock via Distributed Locking (`SET resource_lock my_random_token NX PX 5000`)**. Only the first thread acquires the lock to generate and cache the query; the other 499 threads wait or serve stale data with probabilistic early expiration (XFetch algorithm).
4. **Token-Bucket Rate Limiting**:
   - Use Redis Sorted Sets (`ZADD`, `ZREMRANGEBYSCORE`) to track request timestamps per client IP. Ensures no user exhausts the corporate Groq API quota.

---

### Where Exactly Would Redis Fit Into THIS Project?
1. **Semantic Query Result Cache (`query_cache:<md5_prompt>`)**:
   - Common queries like *"Top 5 spending customers"* or *"Monthly revenue"* are asked repeatedly.
   - Caching the generated SQL and tabular results in Redis with a 30-minute TTL reduces LLM API costs by up to 60% and drops response latency from 300ms to **1.5ms**.
2. **Schema Metadata Cache (`metadata:tables:all`)**:
   - Cache the 22 table definitions and foreign key relationship graph in Redis Hashes.
   - Eliminates redundant file reading and database introspection across multiple worker pods.
3. **Session & Rate-Limiting Store (`ratelimit:<user_or_ip>`)**:
   - Restrict each client to 30 queries per minute to prevent denial-of-wallet attacks against Groq API keys.

---

# 11. RabbitMQ: Message Queuing & Task Decoupling

> 🟢 **CURRENT IMPLEMENTATION**: RabbitMQ is **not currently used**. All request processing is handled synchronously within the HTTP thread.  
> 🟡 **RECOMMENDED IMPROVEMENT**: RabbitMQ should be introduced to decouple heavy report generation, bulk CSV exports, and automated notification dispatches.

---

### RabbitMQ Core Concepts
RabbitMQ is a traditional Advanced Message Queuing Protocol (AMQP) message broker optimized for reliable, low-latency, point-to-point task routing.

```text
[ Producer ] ──► [ Exchange ] ──(Routing Key)──► [ Queue ] ──► [ Consumer Worker ]
                    │                               │
                    ├── Direct (Exact match)        └── DLQ (Dead Letter Queue on failure)
                    ├── Topic (Wildcard pattern)
                    └── Fanout (Broadcast all)
```

- **Producer**: The application code sending a message (e.g. FastAPI route).
- **Exchange**: Message router. Inspects routing keys and delivers messages to bound queues:
  - *Direct Exchange*: Matches routing key exactly (e.g. `reports.csv`).
  - *Topic Exchange*: Matches routing key with wildcards (`reports.*`, `audit.#`).
  - *Fanout Exchange*: Broadcasts message to all bound queues simultaneously.
- **Queue**: Buffer in memory/disk storing messages until consumers acknowledge them.
- **Consumer**: Background worker process (e.g. Celery worker) that pops messages and executes work.
- **Acknowledgements (ACK / NACK)**:
  - Consumer sends `basic.ack` only after successfully processing and writing the report.
  - If a worker crashes midway, RabbitMQ automatically re-queues the message for another worker.
- **Dead-Letter Queue (DLQ)**: If a message fails processing after 3 retry attempts, it is routed to an `x-dead-letter-exchange` for manual inspection, preventing toxic messages from blocking the queue.
- **At-Least-Once Delivery & Idempotency**: RabbitMQ guarantees delivery, but network retries can cause duplicate messages. Consumers must be idempotent (e.g., checking if `report_id` already exists in storage before re-generating).

---

### Where Would RabbitMQ Fit in THIS Project?
**Concrete Use Case: Asynchronous Bulk Analytical Export & Slack Notification**
1. An executive types: *"Export complete 5-year order history with supplier margins to CSV and send to Slack."*
2. This query scans 500,000 records and takes 45 seconds. Running this in a synchronous HTTP request would trigger a browser timeout (HTTP 504 Gateway Timeout).
3. **RabbitMQ Pipeline**:
   - FastAPI endpoint immediately generates a `job_id`, publishes a message to RabbitMQ exchange `analytics.exchange` with routing key `report.generate`, and returns HTTP 202 Accepted: `{"job_id": "abc-123", "status": "queued"}`.
   - A dedicated Python Celery consumer worker pulls the task, executes the query in the background, writes the CSV to S3, and posts the download link to the executive's Slack channel.

---

# 12. Kafka: Event Streaming & Kafka vs RabbitMQ Analysis

> 🟢 **CURRENT IMPLEMENTATION**: Apache Kafka is **not currently used**.  
> 🟡 **RECOMMENDED IMPROVEMENT**: Kafka could serve as a centralized audit event stream if query events need to be ingested into an enterprise data lake.

---

### Kafka Core Concepts
Apache Kafka is a distributed, horizontally partitioned, replicated commit-log event streaming platform designed for ultra-high throughput (millions of events per second).

```text
[ Topic: query_audit_events ]
  ├── Partition 0: [Msg 0][Msg 1][Msg 2][Msg 3] ──► Consumer Group: Analytics (Worker 1)
  ├── Partition 1: [Msg 0][Msg 1][Msg 2]        ──► Consumer Group: Analytics (Worker 2)
  └── Partition 2: [Msg 0][Msg 1][Msg 2][Msg 3] ──► Consumer Group: Security Auditing (Worker 1)
```

- **Topic**: Category feed to which records are published.
- **Partitions**: Topics are broken into ordered, immutable sequences of messages spread across broker nodes. Partitions are the unit of parallelism in Kafka.
- **Offsets**: Each message in a partition is assigned an integer offset (`0, 1, 2, ...`). Consumers track their own offset position.
- **Consumer Groups**: Multiple consumers share the load. Each partition is consumed by exactly one consumer within a group.
- **Retention**: Messages are retained on disk for a configured period (e.g. 7 days), regardless of whether they have been read. Multiple distinct consumer groups can read the same stream independently at their own pace.

---

### Kafka vs RabbitMQ: Which Would You Choose for THIS Project?

| Feature | RabbitMQ | Apache Kafka |
| :--- | :--- | :--- |
| **Architecture** | Smart broker, dumb consumer (broker tracks state & ACKs) | Dumb broker, smart consumer (append-only commit log) |
| **Data Retention** | Messages deleted immediately after consumer ACK | Persistent log retained on disk (days/months) |
| **Throughput** | ~20,000 to 50,000 msgs/sec | 1,000,000+ msgs/sec |
| **Routing Flexibility**| Complex routing (Topic, Direct, Fanout, Headers) | Basic partition key routing |
| **Replayability** | Cannot replay acknowledged messages | Consumers can rewind offsets to replay historical events |
| **Operational Overhead**| Low to Moderate | High (requires ZooKeeper / KRaft quorum, partition tuning) |

### The Definitive Interview Answer:
> *"For NexSQL, **RabbitMQ is the superior architectural choice**.  
> Our primary asynchronous requirement is task decoupling: running long-running reports, background query retries, and scheduled exports. RabbitMQ excels at transient task routing, granular per-message acknowledgements, dead-lettering, and priority queues with minimal operational complexity.  
> We would only select Kafka if NexSQL were expanded to ingest high-frequency clickstream telemetry or CDC (Change Data Capture) database mutation logs at a volume of hundreds of thousands of events per second requiring stream replay."*

---

# 13. Synchronous vs Asynchronous Processing & Concurrency

### Current Implementation Code Analysis
In `backend/app.py`, endpoint routes are defined as standard synchronous Python functions:
```python
@app.post("/api/query")
def execute_nl_query(req: QueryRequest):
    ...
```
- **How FastAPI Handles This**: Because `execute_nl_query` is defined with `def` rather than `async def`, FastAPI does **not** block the main asyncio event loop! Starlette automatically delegates synchronous routes to an external threadpool (`anyio.to_thread.run_sync`).
- **Why it matters**: If an endpoint takes 300ms to communicate with Groq, other concurrent HTTP requests can still be accepted on the event loop.

---

### Concurrency Theory for Technical Interviews
- **CPU-Bound vs I/O-Bound Workloads**:
  - *I/O-Bound*: Waiting on network sockets or disk (e.g. waiting for Groq API response or SQLite disk read). Python's `asyncio` or thread pools excel here because threads can yield while waiting.
  - *CPU-Bound*: Heavy number crunching or AST parsing (e.g. `sqlglot.parse()`). In Python, CPU-bound workloads are constrained by the Global Interpreter Lock (GIL). Running CPU-intensive tasks on multiple threads in Python does not speed them up; they must be offloaded to multiple OS processes via `multiprocessing` or Celery.
- **Race Conditions**: Occur when two concurrent threads read and mutate shared state without synchronization, causing unpredictable final state.
- **Deadlocks**: Occur when Thread A holds Lock 1 and waits for Lock 2, while Thread B holds Lock 2 and waits for Lock 1. Neither can proceed.
  - *SQLite Deadlock Example*: Thread 1 starts an exclusive transaction; Thread 2 attempts to write. If timeout expires, SQLite throws `database is locked`.

---

# 14. Load Balancing & High Availability

- **Layer 4 (Transport) vs Layer 7 (Application) Load Balancing**:
  - *Layer 4 (TCP/UDP)*: Routes packets based on IP address and port without inspecting HTTP headers. Ultra-fast, lower CPU overhead (e.g., AWS Network Load Balancer / HAProxy).
  - *Layer 7 (HTTP/HTTPS)*: Inspects HTTP headers, cookies, URL paths, and methods. Enables path-based routing (e.g. routing `/api/query` to LLM worker pods and `/static/` to CDN). AWS Application Load Balancer operates at Layer 7.
- **Routing Algorithms**:
  - *Round Robin*: Requests sent sequentially (`1, 2, 3, 1, 2, 3`). Good when requests have identical computational cost.
  - *Least Connections*: Routes traffic to the server with the fewest active connections. **Best for NexSQL**, because query latency varies widely (simple queries take 10ms; multi-join queries take 400ms).
- **Health Checks & Failover**:
  - Load balancer pings `GET /healthz` every 5 seconds.
  - If server pod 2 fails 3 consecutive checks (returns 5xx or times out), the load balancer removes it from the target pool immediately.
- **Sticky Sessions vs Stateless Services**:
  - *Sticky Sessions*: Routes repeat requests from the same client to the same physical server based on a session cookie.
  - *Why We Avoid Sticky Sessions*: NexSQL application servers are strictly **stateless**. No session state is held in Python memory. API keys and state are passed in the HTTP request payload or stored in Redis, allowing any server pod to handle any request.

---

# 15. CI/CD & DevOps Engineering

> 🟢 **CURRENT IMPLEMENTATION**: No automated CI/CD pipeline or Dockerfile currently exists in the workspace.  
> 🟡 **RECOMMENDED IMPROVEMENT**: Below is the production-ready CI/CD automation pipeline.

---

### Production CI/CD Pipeline Architecture

```text
[ Developer Git Push (main / PR) ]
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Continuous Integration (GitHub Actions)                   │
│    ├── Linting & Formatting: ruff / black / flake8          │
│    ├── Type Checking: mypy backend/                         │
│    ├── Security Scanning: bandit -r backend/ & pip-audit    │
│    └── Automated Test Suite: pytest tests/test_engine.py    │
│        (Runs 13 unit tests & 20-query benchmark validation) │
└──────────────────────────────┬──────────────────────────────┘
                               │ All Tests Pass
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Container Build & Packaging                               │
│    ├── Multi-Stage Dockerfile Build                         │
│    ├── Container Security Scan: Trivy (Vulnerability scan)  │
│    └── Push Image to Container Registry (Amazon ECR / GHCR) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Continuous Deployment (Kubernetes / ECS)                  │
│    ├── Rolling Update Strategy (Zero Downtime)               │
│    ├── Health Check Verification (GET /healthz)              │
│    └── Automatic Rollback if Error Rate > 1%                 │
└─────────────────────────────────────────────────────────────┘
```

### Production Dockerfile (`RECOMMENDED IMPROVEMENT`)
```dockerfile
# Multi-stage build for minimal attack surface and small image size
FROM python:3.14-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libsqlite3-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.14-slim AS runner
WORKDIR /app
# Run as non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/api/schema').raise_for_status()"
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Zero-Downtime Deployment Strategies:
- **Rolling Deployment**: Gradually replaces old pods with new pods (e.g. 25% at a time). Ensures capacity is never zero.
- **Blue-Green Deployment**: Spawns an entire parallel environment ("Green") with the new code. After smoke tests pass, router switches 100% of traffic from "Blue" to "Green". Instant rollback by switching router back.
- **Canary Deployment**: Routes 5% of real user traffic to the new version. Monitored for error spikes; if error rate remains flat, traffic scales to 100%.
"""
