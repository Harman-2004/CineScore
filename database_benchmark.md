# CineScore PostgreSQL Database Performance Report

This report evaluates the performance metrics of the PostgreSQL database layer under movie search workloads.

## I. System Status & Network Connectivity
- **Target PostgreSQL Database**: Neon Serverless Postgres
- **Host**: `ep-curly-queen-ah2fqhul-pooler.c-3.us-east-1.aws.neon.tech`
- **Connection Status**: `ONLINE (Active)`
- **Database Connection Latency**: `1360.10 ms`

## II. Measured Database Layer Metrics

| Metric | Measured Value | Description |
| :--- | :---: | :--- |
| **Database Connection Time** | 1360.10 ms | Avg time taken to establish database connection. |
| **Avg Query Execution Time** | 378.25 ms | Average execution time taken by PostgreSQL to execute a single SQL query. |
| **Slowest SQL Query** | 2097.45 ms | Latency of the slowest query in the search transaction lifecycle. |
| **Fastest SQL Query** | 267.67 ms | Latency of the fastest cached/indexed select query. |
| **Queries Per Request** | 12.8 | Average number of SQL queries generated per movie search request. |
| **ORM Execution Time** | 378.80 ms | Average overhead introduced by SQLAlchemy ORM compilation/hydration. |

---

## III. PostgreSQL Index Recommendations

Based on schema introspection and search patterns, the following indexes are recommended for maximum database-level optimization:

### 1. JSONB GIN Indexes
The `movies` table contains JSON columns (`genres`, `keywords`, `cast`, `themes`) which are scanned during recommendation matches. Adding GIN indexes will speed up JSON key searches:
```sql
CREATE INDEX idx_movies_genres_gin ON movies USING gin (genres);
CREATE INDEX idx_movies_keywords_gin ON movies USING gin (keywords);
CREATE INDEX idx_movies_cast_gin ON movies USING gin (cast);
CREATE INDEX idx_movies_themes_gin ON movies USING gin (themes);
```

### 2. Composite Query Index
To optimize personalized recommendations cache lookups (filtering by target movie and user):
```sql
CREATE INDEX idx_recommendation_cache_lookup ON recommendation_cache (user_id, recommendation_type);
```
