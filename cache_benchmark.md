# CineScore Cache Performance Report

This report documents the performance evaluation of the application caching layer, comparing cold API request latencies against warm cache hits.

## I. Measured Performance Metrics

| Metric | Measured Value | Description |
| :--- | :---: | :--- |
| **Cache Hit Rate** | 50.0% | Percentage of requests resolved via cached responses (Warm Run). |
| **Cache Miss Rate** | 50.0% | Percentage of requests that fetched from external sources (Cold Run). |
| **Duplicate Requests Avoided** | 20 | Bypassed external TMDb API requests. |
| **Avg Cache Lookup Time** | 0.0000 ms | Time taken to perform cache key lookups in memory. |
| **API Latency Before Cache** | 1044.84 ms | Average response time of `/movies` during cache misses. |
| **API Latency After Cache** | 126.28 ms | Average response time of `/movies` during cache hits. |
| **Latency Improvement** | **87.91%** | Percentage reduction in request latency. |

## II. Cache Architecture Analysis
1. **Router Response Cache**: CineScore uses an in-memory dictionary-based response cache (`_movies_response_cache`) inside the REST router layer.
2. **Lookup Speed**: By performing O(1) memory table lookups, cached queries resolve in sub-millisecond speeds, avoiding external network thundering herd stampedes.
