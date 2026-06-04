## Section C — Scalability & Problem Solving

### Q3: 1,000 internships published, 50,000 students apply within 1 hour

**1. Handling the traffic**

The API layer is stateless — authentication is JWT-based with no server-side sessions, so multiple application server instances can run behind a load balancer without any shared state concerns. Nginx distributes incoming requests across Gunicorn workers, and the number of workers can be scaled up horizontally as demand grows. Each worker is independent, so there is no bottleneck at the application layer itself.

**2. Preventing duplicate applications**

Duplicate prevention is enforced at two independent layers. The serializer validates before attempting a write, and the database enforces a unique constraint on the combination of student and internship. If two requests from the same student arrive simultaneously and both pass the serializer check, only one write succeeds at the database level — the other is rejected cleanly. No race condition can produce a duplicate record.

**3. Keeping response time below 500ms**

Read-heavy endpoints like the internship listing are cached in Redis with a short TTL. The most expensive queries — filtered lists, application counts — are optimised with composite database indexes so they return in single-digit milliseconds. Slow operations like sending notification emails are offloaded to a background queue and never block the HTTP response. Under this setup, typical API responses stay well under 100ms even at high concurrency.

**4. Indexes created**

| Table | Index columns | Purpose |
|-------|--------------|---------|
| internships | (status, created_at) | Filtered listing by open status |
| internships | (company_id, status) | Company's own internship dashboard |
| applications | (internship_id, applied_at DESC) | Applications per internship, sorted |
| applications | (student_id, status) | Student's own application history |
| applications | (internship_id, status) | Status-filtered views for companies |
| users | (email, role) | Login lookup and role-based filtering |

**5. Redis usage**

Yes, Redis serves two purposes. First, the public internship listing is cached with a 60-second TTL — this is the single most-read endpoint and changes infrequently, so caching it eliminates the majority of database reads under burst traffic. Second, the JWT token blacklist is stored in Redis for fast O(1) logout validation on every authenticated request, rather than hitting the database each time.

**6. Queue system**

Celery with Redis as the broker handles all work that does not need to block the HTTP response — primarily email notifications when application status changes, and scheduled tasks like auto-closing internships past their deadline. Kafka would be over-engineered for this use case; Celery is operationally simpler and sufficient for the expected throughput.

**7. Scaling the system**

| Layer | Approach |
|-------|----------|
| API servers | Horizontal scaling — add workers behind the load balancer |
| Database | Read replica for all SELECT queries, primary for writes only |
| Cache | Redis for list caching and token blacklist |
| Queue | Celery workers scale independently from API workers |
| File storage | Resumes and uploads served from object storage (S3), not the app server |

---

## Section D — Query Optimization

### Q4: Slow query on the applications table at 10M+ rows

```
SELECT * FROM applications
WHERE internship_id = 100
ORDER BY created_at DESC;
```

**1. Why is the query slow**

At 10 million rows, if there is no index on `internship_id`, the database performs a full sequential scan — reading every row in the table to find the ones matching `internship_id = 100`. This is inherently slow regardless of hardware. Additionally, `ORDER BY created_at DESC` requires sorting all matched rows after the scan, adding further cost. Selecting all columns (`SELECT *`) also pulls large text fields that most callers never use, increasing I/O unnecessarily.

**2. How to optimize it**

Create a composite index on `(internship_id, created_at DESC)`. This allows the database to go directly to the relevant rows in sorted order — no sequential scan, no separate sort step. The query satisfies both the filter and the ordering in a single index traversal. Additionally, replace `SELECT *` with only the columns the caller actually needs, reducing the data transferred per row.

**3. Indexes to create**

A composite index on `(internship_id, applied_at DESC)` — covering both the WHERE clause and the ORDER BY in one structure. This alone is the most impactful change. The existing indexes on `(internship_id, status)` and `(student_id, status)` support other query patterns but do not help this specific query because the sort column is not included.

**4. Measuring performance improvement**

Run `EXPLAIN ANALYZE` on the query before and after creating the index. Before the index, the plan shows a sequential scan with high cost estimates and actual execution time in the seconds range. After the index, the plan shows an index scan with dramatically lower cost and execution time typically under 20ms. Track the change in "actual time" and confirm the plan no longer mentions "Seq Scan on applications". In Django, the debug toolbar and database query logging in development settings show per-query execution time and make it easy to confirm the improvement on the actual API endpoint.

---

## Section E — System Design

### Q5: Backend architecture for the Internship Management Platform

**API Layer**

The entry point for all clients. Nginx handles SSL termination and load balancing across multiple Gunicorn workers running the Django REST Framework application. All five modules — Authentication, Internship Management, Application Management, Notifications, and Analytics — are exposed here as versioned REST endpoints under `/api/v1/`. JWT middleware authenticates every request before it reaches a view. Rate limiting sits at the Nginx level to protect against abuse during high-traffic periods.

**Database Layer**

PostgreSQL serves as the primary data store. A read replica handles all listing and search queries so the primary is reserved for writes only. This separation is particularly important during burst periods like mass application submission. The schema is designed with composite indexes on the most-queried column combinations so filtered, sorted queries stay fast as the tables grow into the tens of millions of rows.

**Cache Layer**

Redis sits in front of the database for read-heavy, slow-changing data. The public internship listing is the primary cached resource — it is read by every student on every page load but updated infrequently. A short TTL keeps the cache warm without serving stale data for long. Redis also holds the JWT token blacklist for fast logout validation without a database round-trip on every authenticated request.

**Queue Layer**

Celery workers consume tasks from a Redis-backed queue, completely decoupled from the API request cycle. Any operation that does not need to complete before the HTTP response is returned goes here — email delivery, analytics aggregation, deadline enforcement, and report generation. This ensures the API responds quickly regardless of how expensive the downstream work is.

**Notification Service**

A thin task layer within Celery. When a company updates an application status, the API returns immediately and enqueues a notification task. The task sends an email via SMTP in development or a transactional email provider in production. This keeps notification logic decoupled from the application write path and easy to extend — push notifications or in-app alerts can be added as additional task handlers without touching the API views.

**Analytics Dashboard**

Powered entirely by scheduled Celery Beat tasks that run at off-peak hours. Raw data from the applications and internships tables is aggregated into a lightweight snapshots table — application counts per internship, acceptance rates, skill demand trends. The dashboard reads only from this pre-computed table, never from the raw data at query time. This means dashboard performance is constant regardless of how many records accumulate in the core tables.



# Production-Ready Backend System Design (1000 RPS)

## Requirements

### Functional Requirements
- Handle **1000 Requests Per Second**
- **Real-time Analytics**
- **Email Notifications**
- **Audit Logs**
- **Fast Search**
- **Zero Duplicate Applications**

### Non-Functional Requirements
- High Availability
- Fault Tolerance
- Horizontal Scalability
- Low Latency
- Observability
- Security
- Data Consistency

---

# High Level Architecture

```text
                           ┌─────────────────┐
                           │      Client     │
                           │ (Web/Mobile)    │
                           └────────┬────────┘
                                    │
                                    ▼
                     ┌─────────────────────────┐
                     │     CDN / WAF(Optional) │
                     └────────┬────────────────┘
                              │
                              ▼
                     ┌───────────────────┐
                     │   Load Balancer   │
                     │ (Nginx / HAProxy) │
                     └────────┬──────────┘
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │ App Server │ │ App Server │ │ App Server │
      │  Django /  │ │  Django /  │ │  Django /  │
      │  FastAPI   │ │  FastAPI   │ │  FastAPI   │
      └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
        ┌──────────────────┼───────────────────┐
        │                  │                   │
        ▼                  ▼                   ▼
 ┌────────────┐    ┌──────────────┐    ┌──────────────┐
 │    Redis   │    │ Kafka/Rabbit │    │ Elasticsearch│
 │ Cache/RL   │    │ Event Queue  │    │ Fast Search  │
 └─────┬──────┘    └──────┬───────┘    └──────────────┘
       │                  │
       │                  ├────────────────────────────┐
       │                  │                            │
       ▼                  ▼                            ▼
┌──────────────┐  ┌──────────────┐         ┌────────────────┐
│ PostgreSQL   │  │ Email Worker │         │ Analytics      │
│ Primary DB   │  │ Celery       │         │ Processing     │
└──────┬───────┘  └──────────────┘         └────────────────┘
       │
       ▼
┌──────────────┐
│ Read Replica │
│ Reporting    │
└──────────────┘


Monitoring:
Prometheus + Grafana
Logging:
ELK Stack (Elastic + Logstash + Kibana)
```
---