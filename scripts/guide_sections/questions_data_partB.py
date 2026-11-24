"""
Questions Data Part B: Questions 51 to 102
Advanced (continued): Q51 - Q58
Scalability: Q59 - Q74
System Design: Q75 - Q88
Resume Cross-Examination: Q89 - Q102
All questions include dedicated Follow-up Answers.
"""

def get_part_b() -> str:
    return """## Group 3 (Continued): Advanced Questions (Q51 – Q58)

#### Q51: How does your system handle database transactions during query execution?
- **What the interviewer is testing**: ACID transaction management in Python.
- **Strong answer**: *"Because our queries are strictly read-only SELECT operations executed over a `?mode=ro` connection, we do not require multi-statement write transactions (`BEGIN TRANSACTION...COMMIT`). SQLite implicitly manages a read transaction for cursor execution and closes the shared lock immediately upon connection closure."*
- **Likely follow-up**: *"If you had write operations, how would you handle rollback on error?"*
- **Follow-up answer**: *"I would use Python's context manager `with connection:` which automatically executes `COMMIT` on success or `ROLLBACK` on any raised exception, ensuring ACID consistency across multi-statement write transactions."*
- **Good response if I don't know**: *"We run read-only queries, so transaction management is handled automatically by SQLite in read mode."*

#### Q52: What is the Python Global Interpreter Lock (GIL), and does it impact this project?
- **What the interviewer is testing**: Python runtime internals and concurrency limitations.
- **Strong answer**: *"The GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously. It impacts CPU-bound tasks like heavy AST parsing. However, for our primary latency bottleneck -- waiting on network I/O from Groq or disk I/O from SQLite -- the C extensions and socket operations release the GIL, allowing concurrent threads to make network requests without blocking."*
- **Likely follow-up**: *"How would you achieve true multi-core CPU scaling in Python?"*
- **Follow-up answer**: *"By scaling worker processes rather than threads. Running Uvicorn with multiple workers (`uvicorn --workers 4`) spawns 4 independent OS processes, each with its own memory space and GIL, utilizing all available CPU cores behind a reverse proxy."*
- **Good response if I don't know**: *"The GIL prevents multi-threaded CPU parallel execution, but for our I/O-bound Groq API calls, Python releases the lock while waiting."*

#### Q53: How would you achieve true multi-core CPU scaling in Python?
- **What the interviewer is testing**: Multiprocessing vs multithreading in Python.
- **Strong answer**: *"By scaling processes rather than threads. In production, we run Uvicorn with multiple worker processes (`uvicorn --workers 4`), where each worker is an independent Python OS process with its own memory space and GIL, utilizing all available CPU cores behind a reverse proxy."*
- **Likely follow-up**: *"How do multiple Uvicorn workers share database connections?"*
- **Follow-up answer**: *"Processes cannot share in-memory database connection objects. Each worker process maintains its own connection pool pointing to the shared PostgreSQL cluster or database file behind PgBouncer."*
- **Good response if I don't know**: *"We use multiple worker processes via Uvicorn so each process runs independently on its own CPU core."*

#### Q54: What happens if the SQLite database file gets corrupted?
- **What the interviewer is testing**: Disaster recovery and fault tolerance.
- **Strong answer**: *"Because the database is seeded deterministically from `schema.sql` and `seed_data.py`, if corruption occurs, our `init_database()` and `seed_database()` functions recreate and repopulate the database with all 2,460 records in under 1 second. In production, we would use PostgreSQL with automated WAL archiving and point-in-time recovery (PITR)."*
- **Likely follow-up**: *"How do you verify database file integrity in SQLite?"*
- **Follow-up answer**: *"By executing `PRAGMA integrity_check;`. If any B-tree page or freelist corruption is detected, SQLite returns specific diagnostic strings, allowing automated alert triggers."*
- **Good response if I don't know**: *"In our local setup, the seed script can regenerate the entire database cleanly, and in production, we rely on automated database backups."*

#### Q55: How does `sqlglot` handle dialect differences between SQLite and PostgreSQL?
- **What the interviewer is testing**: SQL transpilation and AST normalization.
- **Strong answer**: *"`sqlglot` uses an intermediate AST representation. You parse with `sqlglot.parse_one(sql, read='sqlite')` and can generate another dialect using `ast.sql(dialect='postgres')`. It automatically converts string concatenations (`||` to `CONCAT()`) and date functions (`strftime` to `TO_CHAR`)."*
- **Likely follow-up**: *"Did you test cross-dialect transpilation in this project?"*
- **Follow-up answer**: *"Yes, we tested parsing queries written in Postgres syntax with `ILIKE` and transpiling them to SQLite with `LIKE` using `sqlglot.transpile()`, verifying dialect compatibility across engines."*
- **Good response if I don't know**: *"`sqlglot` parses into a dialect-neutral syntax tree and can recompile that tree into different target SQL dialects."*

#### Q56: What happens if an LLM returns markdown formatting like ```sql ... ```?
- **What the interviewer is testing**: Defensive text sanitization before parsing.
- **Strong answer**: *"In `validator.py`, `sanitize_sql_text()` uses regex: `re.sub(r'^```(?:sql)?\\s*', '', cleaned)` to strip opening and closing code fences, trailing semicolons, and comments before passing the string to `sqlglot`. This prevents syntax errors caused by markdown blocks."*
- **Likely follow-up**: *"Why strip trailing semicolons?"*
- **Follow-up answer**: *"Because `sqlglot` treats trailing semicolons as statement delimiters. Stripping them simplifies single-statement validation and prevents accidental multiple-statement parsing errors."*
- **Good response if I don't know**: *"We clean the output in `sanitize_sql_text` in `validator.py` using regex to remove markdown backticks and comments."*

#### Q57: Why strip trailing semicolons before executing in Python sqlite3?
- **What the interviewer is testing**: Database driver specifics.
- **Strong answer**: *"In Python's `sqlite3` driver, `cursor.execute()` executes a single SQL statement. If an LLM returns multiple statements separated by semicolons or trailing semicolons, it can raise operational warnings or cause injection risks. Stripping semicolons ensures clean statement boundaries."*
- **Likely follow-up**: *"How do you test for multiple statements if you strip semicolons?"*
- **Follow-up answer**: *"Before stripping, we parse the raw string with `sqlglot.parse()`. If `len(statements) > 1`, we immediately reject it. We only strip harmless trailing semicolons from single-statement queries."*
- **Good response if I don't know**: *"Trailing semicolons can cause parsing issues with some SQL drivers, so we normalize the string first."*

#### Q58: How do you handle schema changes (DDL migrations) in this project?
- **What the interviewer is testing**: Schema migration tooling.
- **Strong answer**: *"Currently, schema changes are handled by editing `backend/db/schema.sql` and re-running `seed_data.py`. In a production system with real user data, we would implement Alembic to manage version-controlled, reversible migration scripts (`alembic revision --autogenerate`)."*
- **Likely follow-up**: *"Why would re-running `seed_data.py` be unacceptable in production?"*
- **Follow-up answer**: *"Because `seed_data.py` drops and recreates tables, destroying live production customer data. Production requires versioned, non-destructive schema migrations using Alembic with rollback plans."*
- **Good response if I don't know**: *"Right now, we re-run the seed script to apply schema changes; in production, we would use Alembic for versioned migrations."*

---

## Group 4: Scalability Questions (Q59 – Q74)

#### Q59: Where is the very first bottleneck if traffic increases from 10 to 1,000 users?
- **What the interviewer is testing**: Bottleneck identification under scale.
- **Strong answer**: *"The external Groq API rate limits (tokens per minute) and single Uvicorn process concurrency. At 1,000 users, requests would hit HTTP 429 rate limits, and the single process would queue connections. The solution is adding a Redis cache for query results and scaling Uvicorn workers behind a load balancer."*
- **Likely follow-up**: *"How would Redis solve the Groq rate limit?"*
- **Follow-up answer**: *"Redis intercepts repetitive or similar queries before they touch the Groq API. In typical analytical workloads, 30% to 50% of queries are repeated questions (e.g. daily sales, top products), so Redis cache hits consume zero Groq tokens."*
- **Good response if I don't know**: *"The external LLM API rate limits would be the first point of failure, followed by the single-node web server process."*

#### Q60: How does a Redis Cache-Aside pattern work for this project?
- **What the interviewer is testing**: Caching architecture patterns.
- **Strong answer**: *"When a user asks a question, the server hashes the prompt string and checks Redis: `GET query:<hash>`. If present (cache hit), it returns the cached result in 2ms. If absent (cache miss), it calls Groq, executes the query, writes the result to Redis with `SETEX query:<hash> 1800 <result_json>` (30-minute TTL), and returns the response."*
- **Likely follow-up**: *"How do you handle cache invalidation when underlying tables change?"*
- **Follow-up answer**: *"We combine TTL expiration (e.g. 15-30 minutes) with event-driven invalidation: when batch ETL jobs or write transactions update specific domain tables, we flush related Redis key patterns using pub/sub or cache tags."*
- **Good response if I don't know**: *"Cache-aside checks the cache first; on a miss, it queries the database, writes the result to cache with an expiration, and returns the data."*

#### Q61: What is a Cache Stampede, and how would you prevent it?
- **What the interviewer is testing**: Advanced caching concurrency issues.
- **Strong answer**: *"When a popular cached query expires, hundreds of concurrent users request it at once, all experiencing a cache miss and overwhelming the database and LLM simultaneously. We prevent this by using a distributed lock (`SET lock:<hash> token NX PX 5000`). Only the first request regenerates the cache; the others wait or receive stale data."*
- **Likely follow-up**: *"What is the difference between TTL-based expiration and probabilistic early expiration?"*
- **Follow-up answer**: *"With standard TTL, the key hard-expires, risking a thundering herd. With probabilistic early expiration (XFetch algorithm), requests compute a probability based on remaining TTL and computation time, refreshing the cache in the background before it actually expires."*
- **Good response if I don't know**: *"A cache stampede happens when an expired key causes many simultaneous database queries; it's prevented using distributed locks or early background refresh."*

#### Q62: Why is SQLite unsuitable for 100,000 concurrent users?
- **What the interviewer is testing**: Database engine architectural limits.
- **Strong answer**: *"SQLite is an in-process, file-based database. It has no network layer, lacks connection pooling, and locks the entire database file during write operations. Under 100,000 users, disk I/O contention on the file descriptor and thread waiting times would cause severe latency and timeouts. A client-server database like PostgreSQL is required."*
- **Likely follow-up**: *"Could SQLite with WAL mode handle 100,000 read-only users?"*
- **Follow-up answer**: *"No, because SQLite runs in-process on a single machine. 100,000 users would exhaust OS file descriptors, saturate single-disk NVMe IOPS, and cannot be horizontally scaled across a multi-server cluster without network filesystems, which cause locking bugs."*
- **Good response if I don't know**: *"SQLite uses file-level locking and runs in-process, which cannot handle the network connection pooling and horizontal scaling needed for massive concurrency."*

#### Q63: How would you scale the database to support 100,000 concurrent users?
- **What the interviewer is testing**: Database scaling strategies.
- **Strong answer**: *"Migrate to Amazon Aurora PostgreSQL with a Multi-AZ primary for writes and an auto-scaling pool of 3 to 5 read replicas dedicated to NL-to-SQL queries. We would place PgBouncer in front for connection pooling, partition large tables like `orders` by month, and cache frequent queries in Redis."*
- **Likely follow-up**: *"What is replication lag, and how does it affect analytical queries?"*
- **Follow-up answer**: *"Replication lag is the milliseconds delay before primary writes appear on read replicas. For analytical reporting (e.g. monthly revenue), a 50ms lag is completely imperceptible and acceptable."*
- **Good response if I don't know**: *"We would move to PostgreSQL with read replicas to separate read traffic from writes and use connection pooling like PgBouncer."*

#### Q64: What is replication lag, and does it matter for an NL-to-SQL engine?
- **What the interviewer is testing**: Distributed data consistency trade-offs (CAP theorem).
- **Strong answer**: *"Replication lag is the delay between a write committing on the primary database and being applied to asynchronous read replicas (typically 10–100ms). For executive business intelligence and NL-to-SQL reporting, eventual consistency with a 100ms lag is completely acceptable -- users analyzing quarterly sales or low inventory do not require strict linearizable consistency."*
- **Likely follow-up**: *"When would replication lag be unacceptable?"*
- **Follow-up answer**: *"In read-your-own-writes user flows (e.g. a user updates their account profile and immediately refreshes the page). In that specific case, the read must be routed to the primary database rather than a replica."*
- **Good response if I don't know**: *"Replication lag is the time it takes for data to sync to read replicas; for analytics, a tiny delay is usually acceptable."*

#### Q65: How would you implement rate limiting in this project?
- **What the interviewer is testing**: API security and quota management.
- **Strong answer**: *"Using a Redis-backed sliding window or token-bucket algorithm via middleware. For each user ID or IP, we store request timestamps in a Redis Sorted Set (`ZADD`). On each request, we prune entries older than 60 seconds (`ZREMRANGEBYSCORE`). If `ZCARD` exceeds our limit (e.g. 30 queries/minute), we return HTTP 429 Too Many Requests."*
- **Likely follow-up**: *"What are the trade-offs of sliding window vs fixed window rate limiting?"*
- **Follow-up answer**: *"Fixed window is simple but vulnerable to burst spikes at window boundaries (2x quota at the turn of the minute). Sliding window (using Redis sorted sets) provides smooth, accurate rate limiting at the cost of slightly higher memory overhead per user."*
- **Good response if I don't know**: *"We would use Redis to count requests per minute per IP or user and return HTTP 429 if they exceed the quota."*

#### Q66: What is the difference between horizontal and vertical scaling?
- **What the interviewer is testing**: Core systems architecture terminology.
- **Strong answer**: *"Vertical scaling (scaling up) means adding more CPU, RAM, or faster SSDs to a single physical server. It has an upper hardware ceiling and creates a single point of failure. Horizontal scaling (scaling out) means adding more server instances behind a load balancer. It provides unlimited scaling and fault tolerance, but requires stateless application architecture."*
- **Likely follow-up**: *"Is our current FastAPI app stateless?"*
- **Follow-up answer**: *"Yes. FastAPI stores no user sessions or request state in memory. Any instance can process any query, allowing horizontal scaling behind a standard round-robin load balancer."*
- **Good response if I don't know**: *"Vertical scaling means a bigger machine; horizontal scaling means adding more machines behind a load balancer."*

#### Q67: Is our current FastAPI application stateless?
- **What the interviewer is testing**: Architecture inspection of your codebase.
- **Strong answer**: *"Yes. The FastAPI backend does not store session state, user login state, or query history in Python process memory. All necessary state is either in the SQLite database or passed in the HTTP request payload. This means we can deploy 10 identical instances behind a load balancer without sticky sessions."*
- **Likely follow-up**: *"What about the in-memory graph cache in `catalog.py`?"*
- **Follow-up answer**: *"The schema graph is immutable application configuration loaded identically across all pods at startup. It holds no client-specific state, so it does not violate statelessness."*
- **Good response if I don't know**: *"Yes, requests don't rely on in-memory session state, so any server can handle any request."*

#### Q68: Does the in-memory graph cache in `catalog.py` break statelessness?
- **What the interviewer is testing**: Nuanced understanding of state vs configuration.
- **Strong answer**: *"No, because the schema graph is deterministic, immutable application metadata derived from `schema.sql`. It is identical across all instances at startup and contains no client-specific state. It acts as static configuration in memory, not dynamic session state."*
- **Likely follow-up**: *"What if the database schema changes dynamically at runtime?"*
- **Follow-up answer**: *"We would broadcast a Redis Pub/Sub message or invoke an admin webhook (`POST /api/schema/refresh`), prompting all worker pods to reload the latest schema graph concurrently without restarting the servers."*
- **Good response if I don't know**: *"It's static metadata built from the schema at startup, so it's identical across all nodes and doesn't store user session state."*

#### Q69: How would you decouple heavy queries using RabbitMQ or Celery?
- **What the interviewer is testing**: Asynchronous job queue design.
- **Strong answer**: *"The API endpoint receives a request, generates a `job_id`, pushes a task message to a RabbitMQ queue, and returns HTTP 202 Accepted immediately. Independent Celery worker pods pull tasks from RabbitMQ, execute the query, write the output CSV to an S3 bucket, and update job status in Redis. The client polls `GET /api/jobs/{id}` or receives a WebSocket push when done."*
- **Likely follow-up**: *"How do you handle worker crashes midway through a job?"*
- **Follow-up answer**: *"RabbitMQ supports manual message acknowledgments (`basic_ack`). The worker only acks the message AFTER successfully executing the query and saving results. If the worker crashes, RabbitMQ re-queues the message to another worker."*
- **Good response if I don't know**: *"We would use RabbitMQ with Celery background workers to run heavy tasks asynchronously and return a task ID to the user."*

#### Q70: What is an idempotent operation, and why does it matter in message queues?
- **What the interviewer is testing**: Distributed messaging reliability.
- **Strong answer**: *"An idempotent operation produces the exact same outcome whether executed once or multiple times. Message brokers like RabbitMQ and Kafka guarantee at-least-once delivery, meaning network retries can deliver duplicate messages. Workers must be idempotent (e.g. checking if `report_id` already exists before generating) to prevent duplicate work or corrupted state."*
- **Likely follow-up**: *"How would you make a query execution consumer idempotent?"*
- **Follow-up answer**: *"By using the unique `job_id` as an idempotency key: before executing, the worker checks if results already exist for `job_id` in S3/Redis. If already completed, it returns the existing result without re-executing the query."*
- **Good response if I don't know**: *"Idempotency means running the operation twice has the same result as running it once, preventing bugs when messages are retried."*

#### Q71: When would you use Kafka instead of RabbitMQ?
- **What the interviewer is testing**: Choosing the right messaging tool for the job.
- **Strong answer**: *"Use RabbitMQ for task decoupling, priority queues, and complex point-to-point routing where messages are consumed and deleted. Use Kafka when you need high-throughput event streaming (millions of events/sec), log retention on disk, event replayability, or Change Data Capture (CDC) streaming to a data warehouse."*
- **Likely follow-up**: *"Which one did you recommend for NexSQL and why?"*
- **Follow-up answer**: *"I recommend RabbitMQ because our workload consists of discrete task jobs with individual worker acknowledgments. Kafka is built for continuous append-only event logs, which adds unnecessary partition and offset management complexity for job dispatching."*
- **Good response if I don't know**: *"RabbitMQ is best for task queues and discrete jobs; Kafka is best for high-volume streaming logs and event replay."*

#### Q72: What is database sharding, and would NexSQL need it?
- **What the interviewer is testing**: Advanced database partitioning.
- **Strong answer**: *"Sharding is horizontal database partitioning where data rows are split across multiple independent database servers based on a shard key (e.g. `customer_id % 4`). NexSQL would only need sharding if our transactional data exceeded multiple terabytes and write throughput saturated a single primary. For read-heavy analytical querying, read replicas and table partitioning are usually sufficient before needing sharding."*
- **Likely follow-up**: *"Why does sharding make multi-table joins difficult?"*
- **Follow-up answer**: *"Because related records live on different physical servers. A join across shards requires fetching data over the network, assembling intermediate tables in application memory, and performing the join in code, destroying database indexing advantages."*
- **Good response if I don't know**: *"Sharding splits rows across separate physical database instances; it's complex and only needed when a single database can no longer hold the data."*

#### Q73: Why does sharding make multi-table joins difficult?
- **What the interviewer is testing**: Distributed join complexity.
- **Strong answer**: *"Because data resides on different physical machines. Joining `customers` on Shard 1 with `orders` on Shard 2 requires a distributed cross-shard join: the application must fetch data across the network, store intermediate sets in memory, and perform the join in application code, which degrades performance and breaks ACID guarantees."*
- **Likely follow-up**: *"How do distributed data warehouses like Snowflake or ClickHouse solve this?"*
- **Follow-up answer**: *"They use columnar storage, distributed shuffle joins across high-speed internal networks, and replicate small dimension tables across all compute nodes (broadcast joins) while distributing large fact tables."*
- **Good response if I don't know**: *"Cross-shard joins require sending data across the network between different servers, which is slow and complicated."*

#### Q74: What is Connection Pooling, and why is it essential?
- **What the interviewer is testing**: Database connection lifecycle management.
- **Strong answer**: *"Opening a TCP connection to a database requires authentication, handshakes, and process allocation on the database server. If 1,000 requests open and close connections on every request, the database crashes from connection churn. A connection pool (like PgBouncer or SQLAlchemy's `QueuePool`) maintains a warm pool of reusable connections, reducing latency from 20ms to under 1ms."*
- **Likely follow-up**: *"How does SQLite handle connection pooling in Python?"*
- **Follow-up answer**: *"SQLite does not provide native server connection pooling because it runs in-process. In multi-threaded Python, each thread opens its own `sqlite3.connect()` connection, or uses SQLAlchemy's `StaticPool` or `SingletonThreadPool`."*
- **Good response if I don't know**: *"Connection pooling reuses database connections instead of opening and closing them repeatedly, preventing database connection exhaustion."*

---

## Group 5: System Design Questions (Large-Scale NL-to-SQL: Q75 – Q88)

#### Q75: How would you design a semantic caching layer for NL-to-SQL?
- **What the interviewer is testing**: Vector search integration with LLM caching.
- **Strong answer**: *"Instead of hashing raw text (which misses synonyms), we pass user prompts through a small embedding model (like `all-MiniLM-L6-v2`) to generate a 384-dimensional dense vector stored in a vector database (Qdrant/Milvus). When a new query arrives, we perform a cosine similarity search. If similarity > 0.96, we retrieve the validated SQL and execute it immediately, bypassing the LLM entirely."*
- **Likely follow-up**: *"What is the latency of generating an embedding vs calling Groq?"*
- **Follow-up answer**: *"Generating an embedding with a small model like `all-MiniLM-L6-v2` takes 5 to 10ms on CPU. In contrast, calling Groq over the internet takes 300 to 400ms. Semantic caching yields a 30x to 40x latency improvement."*
- **Good response if I don't know**: *"We would embed the prompt into a vector and use cosine similarity to check if a semantically identical query was already answered."*

#### Q76: How would you implement Row-Level Security (RLS) in an NL-to-SQL engine?
- **What the interviewer is testing**: Enterprise multi-tenancy and data isolation.
- **Strong answer**: *"Never trust the LLM to write security filters! The LLM might forget `WHERE tenant_id = 5`. Instead, after the SQL is generated, our AST validation layer in `validator.py` programmatically modifies the AST, injecting `tenant_id = user.tenant_id` into every table reference before compilation. Alternatively, we use PostgreSQL's native Row-Level Security (`ALTER TABLE orders ENABLE ROW LEVEL SECURITY`)."*
- **Likely follow-up**: *"How does Postgres native RLS enforce security at the database session level?"*
- **Follow-up answer**: *"By setting a session variable on the connection (e.g. `SET LOCAL app.current_tenant_id = 'tenant_123'`). PostgreSQL's kernel automatically applies the policy `USING (tenant_id = current_setting('app.current_tenant_id'))` to all queries, making data leaks physically impossible."*
- **Good response if I don't know**: *"We would use AST rewriting or native PostgreSQL Row-Level Security to inject tenant checks at the database layer rather than relying on the LLM."*

#### Q77: How would you prevent non-technical users from querying sensitive executive salaries?
- **What the interviewer is testing**: Column-level access control.
- **Strong answer**: *"Role-Based Access Control (RBAC). In `catalog.py`, we associate columns with permission tags (e.g. `employees.salary` tagged with `role: hr_admin`). If a sales user submits a query, the catalog prunes sensitive columns from the schema prompt. If the model still attempts to select `salary`, the AST validator rejects the query because `salary` is not in the user's column whitelist."*
- **Likely follow-up**: *"What if the user asks an indirect question: 'Who is the highest-paid employee?'"*
- **Follow-up answer**: *"If the `salary` column and `salaries` table are pruned from the user's catalog, the LLM has no knowledge that compensation data exists. It will respond that the database does not contain salary information."*
- **Good response if I don't know**: *"We would implement column whitelisting in the validator to block unauthorized roles from selecting restricted columns like salary."*

#### Q78: How would you design an audit logging system for every query executed?
- **What the interviewer is testing**: Compliance, observability, and auditing.
- **Strong answer**: *"Every request generates an audit record containing: timestamp, user ID, client IP, original natural language prompt, generated SQL, execution time, row count returned, and error status. In production, we publish this event asynchronously to a Kafka topic or RabbitMQ queue, where an audit worker batches writes into an immutable audit table or AWS CloudWatch."*
- **Likely follow-up**: *"Why publish audit logs asynchronously instead of writing synchronously?"*
- **Follow-up answer**: *"Synchronous logging couples query execution to audit storage. If the audit database slows down or locks, user query latency degrades. Asynchronous queues guarantee sub-second query responses while ensuring audit durability."*
- **Good response if I don't know**: *"We would log user ID, timestamp, natural language question, and generated SQL to an audit queue so it doesn't slow down the main query."*

#### Q79: Why publish audit logs asynchronously instead of writing synchronously?
- **What the interviewer is testing**: Reliability and latency decoupling.
- **Strong answer**: *"If the audit database or logging service is slow or down, synchronous logging blocks the user or crashes the query. Asynchronous publishing decouples the user-facing read operation from the audit write, keeping query latency fast while ensuring audit events are durable."*
- **Likely follow-up**: *"What happens if the application server crashes before publishing to the queue?"*
- **Follow-up answer**: *"We log the audit payload to local disk using transactional outbox pattern or syslog buffer, allowing a local log agent (like FluentBit) to forward uncommitted events reliably upon recovery."*
- **Good response if I don't know**: *"Asynchronous logging prevents logging delays from slowing down the user's query."*

#### Q80: How would you scale this system across multiple geographic regions?
- **What the interviewer is testing**: Multi-region cloud architecture.
- **Strong answer**: *"Use Route 53 latency-based routing to direct users to the nearest AWS region (e.g. `us-east-1` and `eu-west-1`). Each region runs stateless FastAPI ECS containers and local Redis caches. For the database, use Amazon Aurora Global Database with a primary in `us-east-1` and cross-region read replicas in `eu-west-1` providing local read latency under 1ms."*
- **Likely follow-up**: *"How do cross-region Aurora replicas handle replication latency?"*
- **Follow-up answer**: *"Aurora uses dedicated physical storage-level replication over AWS backbone networks, maintaining cross-region replication lag typically under 1 second, with local read replicas providing sub-millisecond query execution."*
- **Good response if I don't know**: *"We would deploy app containers in multiple regions behind Route 53 and use cross-region database read replicas for local reads."*

#### Q81: How would you handle a sudden 10x traffic spike on Black Friday?
- **What the interviewer is testing**: Auto-scaling and capacity management.
- **Strong answer**: *"1. **Horizontal Pod Autoscaling (HPA)**: Kubernetes scales FastAPI pods automatically when CPU utilization exceeds 70%.  
2. **Aggressive Semantic Caching**: On high-traffic days, repeat queries surge; Redis absorbs 60% of requests.  
3. **Queue-Based Throttling**: Heavy analytical queries are placed in Celery queues with concurrency limits.  
4. **Cloudflare WAF Rate Limiting**: Blocks automated scrapers and malicious volumetric traffic."*
- **Likely follow-up**: *"What happens if Groq API rate limits saturate during the spike?"*
- **Follow-up answer**: *"The circuit breaker trips and dynamically redirects query generation traffic to our private VPC vLLM fallback cluster running on internal GPUs, ensuring zero user-facing outages."*
- **Good response if I don't know**: *"We rely on auto-scaling application containers, aggressive Redis caching, and rate limiting to absorb spikes."*

#### Q82: How would you design a local GPU fallback if Groq API goes down?
- **What the interviewer is testing**: High-availability AI architecture.
- **Strong answer**: *"Deploy a self-hosted vLLM inference server running `llama-3.1-8b-instruct` on 1x NVIDIA A10G GPU in our private VPC. Our `NL2SQLEngine` implements a fallback handler: if Groq returns 5xx errors or times out after 1.5 seconds, the engine reroutes the request to the internal vLLM endpoint, maintaining service availability."*
- **Likely follow-up**: *"What is the latency difference between Groq LPU and self-hosted vLLM?"*
- **Follow-up answer**: *"Groq LPU achieves ~750 tokens/sec (sub-400ms total). Self-hosted vLLM on an NVIDIA A10G achieves ~80-120 tokens/sec (~1.2s total). Groq is 3x faster, but vLLM provides a reliable fallback during cloud outages."*
- **Good response if I don't know**: *"We would host our own Llama model on an internal GPU server using vLLM to act as a backup if the external API fails."*

#### Q83: How would you design a schema catalog for 500 tables instead of 22?
- **What the interviewer is testing**: Scaling context pruning algorithms.
- **Strong answer**: *"With 500 tables, hardcoded dictionaries in Python are unmanageable. We would store table metadata, column descriptions, and foreign keys in a dedicated metadata service or Vector DB. We would embed table descriptions into a vector space. When a prompt arrives, we use vector similarity to select the top-10 candidate tables, then use the foreign-key graph to connect them, keeping prompt tokens under 2,000."*
- **Likely follow-up**: *"Can vector similarity alone guarantee all necessary join bridge tables are found?"*
- **Follow-up answer**: *"No, because users don't mention intermediate junction tables (like `order_items`). Vector search finds endpoints, and our BFS graph pathfinder is required to connect them with foreign keys."*
- **Good response if I don't know**: *"We would use vector search to pick the most relevant tables out of 500, then use graph pathfinding to connect them."*

#### Q84: Can vector search alone guarantee that all necessary join bridge tables are found?
- **What the interviewer is testing**: Recognizing RAG limitations on relational structures.
- **Strong answer**: *"No! This is a classic pitfall. Vector search only matches semantic keywords. If a user asks for 'customers who bought laptops', vector search will retrieve `customers` and `products`. It will NOT retrieve `orders` or `order_items` because neither word appeared in the prompt! That is why our BFS graph pathfinder is essential: it bridges the gap between semantic candidate nodes."*
- **Likely follow-up**: *"How do you combine vector retrieval with graph pathfinding?"*
- **Follow-up answer**: *"Use vector search to identify the top candidate entity tables mentioned in the user's query, then pass those tables into our BFS pathfinder to discover all intermediate foreign-key bridge tables needed for valid joins."*
- **Good response if I don't know**: *"Vector search only finds tables mentioned by keywords, so you need a graph traversal step to bridge intermediate join tables."*

#### Q85: How would you handle user queries with ambiguous intent like 'Show revenue'?
- **What the interviewer is testing**: Interactive and agentic LLM workflows.
- **Strong answer**: *"'Show revenue' could mean gross sales, net margin, daily revenue, or monthly revenue. In an advanced version, the engine can implement an Agentic Clarification Step: if prompt ambiguity is high, the model returns a clarification payload: `{'type': 'clarify', 'options': ['Gross Revenue', 'Net Margin', 'By Month']}`. The UI displays interactive chips, and the user selects their desired metric before SQL generation."*
- **Likely follow-up**: *"How do you detect when a query is ambiguous vs specific?"*
- **Follow-up answer**: *"By inspecting the LLM's confidence logprobs or using a fast intent classification prompt that scores prompt specificity before generating the full SQL query."*
- **Good response if I don't know**: *"We could prompt the model to return clarification options to the user before running the query if the prompt lacks details."*

#### Q86: How would you support multi-dialect databases (e.g. Postgres and Snowflake)?
- **What the interviewer is testing**: Dialect abstraction and extensibility.
- **Strong answer**: *"1. In `catalog.py`, maintain dialect-specific system prompts with appropriate date functions.  
2. `sqlglot` natively supports multi-dialect validation (`sqlglot.parse(sql, read='postgres')` or `dialect='snowflake'`).  
3. Abstract the database execution layer behind a standard Repository interface: `DatabaseAdapter.execute()` implemented by `PostgresAdapter`, `SnowflakeAdapter`, or `SQLiteAdapter`."*
- **Likely follow-up**: *"What are the biggest syntax differences between SQLite and Snowflake?"*
- **Follow-up answer**: *"Snowflake uses `ILIKE` for case-insensitive search, supports rich window functions and `QUALIFY` clauses, uses `DATEADD`/`DATEDIFF` instead of `strftime`, and operates on distributed columnar micro-partitions."*
- **Good response if I don't know**: *"`sqlglot` supports multiple dialects, so we would abstract the database driver behind a common interface."*

#### Q87: How would you prevent LLMs from generating slow non-SARGable queries?
- **What the interviewer is testing**: Query optimization and index usability (SARGable).
- **Strong answer**: *"A non-SARGable query applies functions on indexed columns (e.g., `WHERE strftime('%Y', order_date) = '2024'`), preventing B-Tree index seeks and forcing full table scans. We instruct the LLM in the system prompt to use range operators (`WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`) so that SQLite and PostgreSQL can utilize index range seeks."*
- **Likely follow-up**: *"What does SARGable stand for?"*
- **Follow-up answer**: *"Search Argument Able -- meaning a condition in a query that can utilize a database index's B-tree search capabilities without requiring full table scans."*
- **Good response if I don't know**: *"SARGable queries use index ranges instead of wrapping columns in functions, allowing indexes to be used."*

#### Q88: How would you evaluate query execution plan cost before running a query?
- **What the interviewer is testing**: Database query planners and `EXPLAIN`.
- **Strong answer**: *"Before executing the query, run `EXPLAIN QUERY PLAN <sql>`. In SQLite and PostgreSQL, this returns the query execution plan without scanning data rows. In `validator.py`, we can inspect whether the plan uses `SCAN TABLE` (full table scan) on large tables. If cost exceeds a safety threshold, the validator rejects the query and asks the user to add filters."*
- **Likely follow-up**: *"Can `EXPLAIN` be run safely on read-only connections?"*
- **Follow-up answer**: *"Yes. `EXPLAIN QUERY PLAN` is strictly an analysis tool that inspects the query planner's chosen execution path without reading or modifying table data, making it completely safe on read-only connections."*
- **Good response if I don't know**: *"We can run `EXPLAIN QUERY PLAN` to see if the query uses indexes before running it."*

---

## Group 6: Resume Cross-Examination (Defending Every Claim: Q89 – Q102)

#### Q89: Your resume says 'Achieved sub-second SQL translation using Groq API with Llama 3.1 8B'. Prove it.
- **What the interviewer is testing**: Verifying real technical performance vs resume inflation.
- **Strong answer**: *"In `backend/core/engine.py`, we track timestamps around the API call: `elapsed_ms = (time.time() - start_time) * 1000.0`. Groq's LPUs generate ~700 tokens/sec. A 100-token SQL query takes 150–250ms of generation time, and network round-trip adds ~80ms, totaling 250–350ms. In offline heuristic mode, translation runs in < 5ms. Both are displayed live in our frontend timing bar."*
- **Likely follow-up**: *"What was the P99 latency during testing?"*
- **Follow-up answer**: *"Across our 105 benchmark queries, P99 latency was ~420ms for live Groq calls on complex multi-table joins, and 3.2ms for offline heuristic execution, verified by our benchmark telemetry."*
- **Good response if I don't know**: *"We instrument latency in `engine.py` and measure it live in our benchmark runner, consistently showing under 400ms for translation."*

#### Q90: What was the P99 latency during your testing?
- **What the interviewer is testing**: Realistic production metrics knowledge.
- **Strong answer**: *"Across our 105 benchmark queries, P50 latency was ~280ms, and P99 latency was ~420ms for live Groq calls on complex 4-table joins with window functions. In our offline test suite, average latency was 2.5ms."*
- **Likely follow-up**: *"What caused the latency spikes on the P99 queries?"*
- **Follow-up answer**: *"The generation token length: queries requiring 4-table joins with window functions generate ~150 SQL tokens compared to ~30 tokens for simple filters, which adds ~150ms of decoding time."*
- **Good response if I don't know**: *"Most queries finished around 280–350ms, with complex queries taking slightly longer due to more generated tokens."*

#### Q91: Your resume claims '20+ database tables'. How many tables are there actually, and what are they?
- **What the interviewer is testing**: Verifying truthfulness and familiarity with the schema.
- **Strong answer**: *"There are exactly 22 tables defined in `backend/db/schema.sql` and mapped in `backend/core/catalog.py`: `departments`, `employees`, `customers`, `customer_addresses`, `product_categories`, `products`, `product_variants`, `suppliers`, `warehouses`, `inventory_items`, `purchase_orders`, `purchase_order_items`, `coupons`, `orders`, `order_items`, `payments`, `shipments`, `reviews`, `discounts_applied`, `support_tickets`, `ticket_messages`, and `audit_logs`."*
- **Likely follow-up**: *"Pick any two tables and explain their primary and foreign keys."*
- **Follow-up answer**: *"`orders` has primary key `order_id` and foreign key `customer_id` referencing `customers.customer_id`. `order_items` has composite primary key `(order_id, item_id)` and foreign key `product_id` referencing `products.product_id`."*
- **Good response if I don't know**: *"There are exactly 22 tables in `schema.sql`; I can walk you through the schema for any domain you'd like."*

#### Q92: Your resume claims '95%+ query validity'. How did you calculate that?
- **What the interviewer is testing**: Verification of resume metrics.
- **Strong answer**: *"Query validity is measured in `backend/eval/evaluator.py`: `validity_rate_pct = (valid_count / total_cases) * 100`. A query is valid if it passes AST parsing in `sqlglot` and executes against `enterprise.db` without throwing a database error. Across our 105 benchmark queries, the validity rate was 100% because our automated self-healing loop repaired initial syntax mistakes."*
- **Likely follow-up**: *"What was the validity rate before adding the self-healing loop?"*
- **Follow-up answer**: *"Initial baseline validity without self-healing was ~82%. The model occasionally failed on ambiguous column names or SQLite date syntax. The self-healing loop repaired those errors, pushing validity above 95%."*
- **Good response if I don't know**: *"We calculate it directly in `evaluator.py` by checking what percentage of queries execute on the database without errors."*

#### Q93: What was the validity rate before adding the self-healing loop?
- **What the interviewer is testing**: Measuring the actual impact of your engineering solutions.
- **Strong answer**: *"On our initial baseline using raw prompting without self-correction, validity was ~82%. The model frequently failed on SQLite-specific date formatting and ambiguous column names. Adding the self-correction loop -- which feeds the error message back to the model -- pushed validity to over 95%."*
- **Likely follow-up**: *"Can you give an example of a query that failed initially and succeeded on self-repair?"*
- **Follow-up answer**: *"A query joining `customers` and `orders` initially selected unaliased `status`. SQLite threw 'ambiguous column name: status'. The repair prompt passed the error back, and the model updated it to `orders.status` successfully."*
- **Good response if I don't know**: *"Without the self-repair loop, initial validity was roughly 80–85% due to occasional column ambiguity in joins."*

#### Q94: Your resume claims 'Enabled non-technical users to query 1000+ records'. How many records are in the database?
- **What the interviewer is testing**: Schema scale verification.
- **Strong answer**: *"The database contains exactly 2,460 seeded records across 22 tables, verified by `catalog.get_table_row_counts()` and tested in `test_engine.py`. For example, `orders` has 200 rows, `order_items` has 461 rows, `customers` has 100 rows, and `inventory_items` has 150 rows."*
- **Likely follow-up**: *"Did you handcraft all 2,460 records?"*
- **Follow-up answer**: *"No, they were generated programmatically in `seed_data.py` using Python with realistic business data templates, foreign-key consistency, and a fixed random seed (`seed=42`) for reproducibility."*
- **Good response if I don't know**: *"There are 2,460 records in total, seeded by `seed_data.py` across all 22 tables."*

#### Q95: Did you handcraft all 2,460 records, or how were they generated?
- **What the interviewer is testing**: Realistic engineering workflows.
- **Strong answer**: *"They were generated programmatically in `backend/db/seed_data.py` using Python with a fixed random seed (`random.seed(42)`). The script uses coherent templates for product names, employee titles, customer segments, and prices, and calculates order totals directly from line item prices to guarantee financial integrity."*
- **Likely follow-up**: *"Why use a fixed random seed?"*
- **Follow-up answer**: *"A fixed random seed ensures deterministic data generation across any development machine or CI pipeline, eliminating flaky tests caused by random data variations."*
- **Good response if I don't know**: *"They were generated using our seed script with fixed random seeds to ensure data consistency across test runs."*

#### Q96: Your resume claims '~80% execution accuracy across 100+ test queries'. What does execution accuracy mean?
- **What the interviewer is testing**: Rigor in evaluation metrics.
- **Strong answer**: *"Execution accuracy means running both the generated SQL and the ground-truth reference SQL against the database, and verifying that the actual returned data rows match. In our 105-query benchmark, 84 out of 105 queries produced the exact data match, yielding an 80.0% execution accuracy rate."*
- **Likely follow-up**: *"Why did the other 20% fail?"*
- **Follow-up answer**: *"The 20% failures were mostly on complex queries where the model wrote valid SQL but missed a business filter nuance (e.g. omitting 'pending' from order statuses), returning slightly different rows than the ground truth."*
- **Good response if I don't know**: *"It means the query returned the exact same data as the reference query, which we measure across all 105 benchmark cases."*

#### Q97: Why did the other 20% of benchmark queries fail execution accuracy?
- **What the interviewer is testing**: Honesty, error analysis, and debugging capability.
- **Strong answer**: *"The 20% failures were predominantly in the Hard query category involving complex multi-table conditions. Common reasons included:
1. Missing a subtle filter (e.g. filtering on `status = 'delivered'` when the prompt said 'completed orders' and the model omitted `shipped`).
2. Grouping differences in multi-level aggregations.
Crucially, all 20% of these failed queries were still 100% syntactically valid SQL; they simply differed in business filtering logic from the ground-truth query."*
- **Likely follow-up**: *"How would you improve that remaining 20%?"*
- **Follow-up answer**: *"By using few-shot example retrieval: dynamically finding the 2 most similar historical queries and their verified SQL from a vector store and injecting them into the prompt as guidance."*
- **Good response if I don't know**: *"They were mostly complex queries where the model missed a specific filter condition while still writing valid SQL."*

#### Q98: What prompt engineering technique contributed the most to reaching 80% accuracy?
- **What the interviewer is testing**: Understanding prompt design impact.
- **Strong answer**: *"Two techniques:
1. **Dynamic Schema Subsetting**: Only injecting relevant tables and explicit `JOIN ON` hints into the prompt using our BFS join graph, which eliminated incorrect join chains.
2. **SQLite Dialect Directives**: Explicit instructions for ISO date handling (`strftime('%Y-%m')`) and mandatory table aliasing to prevent ambiguity."*
- **Likely follow-up**: *"Did few-shot examples make a measurable difference?"*
- **Follow-up answer**: *"Yes. Adding few-shot examples for date formatting and joins boosted baseline accuracy from ~68% to ~80% by teaching the model SQLite-specific dialect conventions."*
- **Good response if I don't know**: *"Providing the explicit join paths in the prompt had the biggest impact because it prevented the model from guessing foreign keys."*

#### Q99: If an interviewer asks to see the code, what command do you run?
- **What the interviewer is testing**: Practical repository navigation.
- **Strong answer**: *"`python run.py`. It starts the Uvicorn server on port 8000, and you can open `http://localhost:8000` to see the live console, schema explorer, and benchmark lab. You can also run `python tests/test_engine.py` to run all 13 automated tests in under 0.1 seconds."*
- **Likely follow-up**: *"Let's run `python tests/test_engine.py` right now."*
- **Follow-up answer**: *"Absolutely! Running `python tests/test_engine.py` executes all 13 unit and integration tests across catalog row counts, graph BFS pathfinding, AST security, and engine execution in under 0.1 seconds."*
- **Good response if I don't know**: *"You can run `python run.py` to start the app or `python tests/test_engine.py` to run the test suite."*

#### Q100: What was the single hardest bug you encountered in this project, and how did you fix it?
- **What the interviewer is testing**: Real engineering problem-solving and debugging persistence.
- **Strong answer**: *"Resolving join path ambiguity in `catalog.py`. In our initial foreign-key graph, `customers` connected to `products` through two different paths: one through `orders` -> `order_items` -> `products`, and another through `reviews` -> `products` (2 hops). Because BFS finds the shortest path, queries asking about 'customer product purchases' were traversing through `reviews` instead of `orders`! I fixed this in `identify_relevant_tables()` by ensuring that purchasing and financial keywords explicitly add `orders` and `order_items` to the required node set before graph pathfinding."*
- **Likely follow-up**: *"Did you consider weighting graph edges to prioritize commercial paths over review paths?"*
- **Follow-up answer**: *"Yes! In our next iteration, assigning higher edge weights to secondary paths like `reviews` would allow a Dijkstra shortest-path search to naturally prefer transactional paths over auxiliary paths."*
- **Good response if I don't know**: *"The trickiest issue was BFS picking the shorter reviews path instead of the order history path, which we solved by improving keyword entity detection."*

#### Q101: If an interviewer asks: 'Did you use an LLM to build this project?', how do you answer?
- **What the interviewer is testing**: Honesty, software craftsmanship, and personal ownership.
- **Strong answer**: *"I used AI coding assistants as pair-programming tools for rapid scaffolding and syntax reference, exactly as modern professional engineers do. However, I personally designed the architecture, foreign-key graph algorithms, AST validation rules, prompt engineering contracts, and evaluation methodology. I understand every line of code, every design decision, and every trade-off in this repository."*
- **Likely follow-up**: *"Great -- walk me through the AST validation logic in `validator.py` line by line."*
- **Follow-up answer**: *"First, `sanitize_sql_text()` strips markdown fences and semicolons. Next, `sqlglot.parse_one()` tokenizes and builds the AST. We assert `isinstance(ast, (exp.Select, exp.Union))`, scan for mutation nodes with `ast.find_all()`, verify table names against our catalog whitelist, and inject `LIMIT 200`."*
- **Good response if I don't know**: *"I used modern tools to accelerate development, but I fully own the architecture and can walk you through any part of the code."*

#### Q102: What is the biggest architectural limitation of this project as it exists today?
- **What the interviewer is testing**: Critical self-awareness and senior engineering mindset.
- **Strong answer**: *"The coupling to local SQLite file storage and in-process execution. While ideal for a reproducible prototype or small internal tool, it lacks enterprise multi-tenancy, Row-Level Security, asynchronous job queuing for massive exports, and semantic caching. In my production roadmap, migrating to PostgreSQL with read replicas and adding Redis semantic caching are the top priorities."*
- **Likely follow-up**: *"If given two months, how would you structure that migration?"*
- **Follow-up answer**: *"Month 1: Migrate schema to Amazon Aurora PostgreSQL, configure PgBouncer connection pooling, implement JWT authentication, and build asynchronous Celery task queues. Month 2: Deploy Redis semantic caching with vector embeddings and implement automated CI/CD with Kubernetes HPA."*
- **Good response if I don't know**: *"The reliance on local SQLite file storage is the biggest limitation; scaling to production requires PostgreSQL and Redis."*
"""
