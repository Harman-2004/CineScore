# CineScore PostgreSQL Database Performance Report

This report evaluates the performance metrics of the PostgreSQL database layer under movie search workloads.

## I. Measured Performance Metrics

| Metric | Measured Value | Description |
| :--- | :---: | :--- |
| **Database Connection Time** | 1053.36 ms | Avg time to check out a connection from the SQLAlchemy connection pool. |
| **Avg Query Execution Time** | 438.62 ms | Average time taken by PostgreSQL to execute a single SQL query. |
| **Slowest SQL Query** | 2229.88 ms | Latency of the slowest query (often initial cold checkout or complex join). |
| **Fastest SQL Query** | 272.72 ms | Latency of the fastest cached/indexed select query. |
| **Queries Per Request** | 12.8 | Average number of SQL queries generated per movie search request. |
| **ORM Execution Time** | 440.37 ms | Average overhead introduced by SQLAlchemy ORM compilation/hydration. |

## II. PostgreSQL Index Recommendations

Based on schema introspection and search patterns, the following indexes are recommended for maximum optimization:

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
