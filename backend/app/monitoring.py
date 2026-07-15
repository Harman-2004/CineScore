# monitoring.py
# Core performance monitoring module for CineScore.
# Tracks DB, ORM, external API latency, CPU/memory usage, and generates structured logs.

import contextvars
import time
import os
import json
import threading
from collections import deque
import datetime
from typing import Optional, List, Dict, Any, Callable
import logging

import psutil
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
import httpx
import requests
from fastapi.routing import APIRoute
from fastapi import Request, Response

logger = logging.getLogger("cinescore.monitoring")

# ContextVar to store request-specific metrics
metrics_context = contextvars.ContextVar("metrics_context", default=None)

# Global metrics history for dashboard stats (thread-safe)
GLOBAL_METRICS_LOCK = threading.Lock()
GLOBAL_METRICS_HISTORY = deque(maxlen=2000)

# Global startup time record
STARTUP_TIME = time.time()

# File paths for logs
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
PERFORMANCE_LOG_PATH = os.path.join(LOGS_DIR, "api_performance.log")

class RequestMetrics:
    def __init__(self, method: str, path: str):
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        self.method = method
        self.path = path
        self.movie_name = "N/A"
        self.start_time = time.time()
        self.end_time = None
        self.api_response_time = 0.0
        self.endpoint_duration = 0.0
        
        # Database / ORM
        self.db_queries_count = 0
        self.db_queries_duration = 0.0
        self.orm_duration = 0.0
        
        # External APIs
        self.tmdb_calls_count = 0
        self.tmdb_duration = 0.0
        self.omdb_calls_count = 0
        self.omdb_duration = 0.0
        self.youtube_calls_count = 0
        self.youtube_duration = 0.0
        self.network_wait_duration = 0.0 # Time spent waiting on network calls
        
        # AI Components
        self.sentiment_calls_count = 0
        self.sentiment_duration = 0.0
        self.embedding_calls_count = 0
        self.embedding_duration = 0.0
        self.recommendation_duration = 0.0
        
        # Cache
        self.cache_hits = 0
        self.cache_misses = 0
        
        # System usage
        self.process = psutil.Process(os.getpid())
        try:
            # First call to cpu_percent initializes it
            self.process.cpu_percent(interval=None)
            self.start_mem = self.process.memory_info().rss / (1024 * 1024) # MB
        except Exception:
            self.start_mem = 0.0
            
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.status_code = 200

    def finalize(self, status_code: int):
        self.end_time = time.time()
        self.api_response_time = self.end_time - self.start_time
        self.status_code = status_code
        try:
            self.cpu_usage = self.process.cpu_percent(interval=None)
            self.memory_usage = self.process.memory_info().rss / (1024 * 1024) # MB
        except Exception:
            self.cpu_usage = 0.0
            self.memory_usage = self.start_mem

def get_current_metrics() -> Optional[RequestMetrics]:
    return metrics_context.get()

def initialize_monitoring():
    """Initializes HTTP clients patching and SQLAlchemy event hooks."""
    # Ensure logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 1. Patch requests.Session.request (sync HTTP calls)
    _patch_sync_requests()
    
    # 2. Patch httpx.AsyncClient.send (async HTTP calls)
    _patch_async_httpx()
    
    # 3. Setup SQLAlchemy listeners
    _setup_sqlalchemy_listeners()
    
    # 4. Patch service level functions
    _patch_services()
    
    logger.info("CineScore performance monitoring successfully initialized.")

def _patch_services():
    # A. Sentiment Service
    try:
        from app.sentiment.analyzer import sentiment_service
        original_analyze = sentiment_service.analyze_text
        
        def instrumented_analyze_text(text: str) -> Dict[str, Any]:
            metrics = get_current_metrics()
            start = time.time()
            try:
                return original_analyze(text)
            finally:
                duration = time.time() - start
                if metrics:
                    metrics.sentiment_calls_count += 1
                    metrics.sentiment_duration += duration
                    
        sentiment_service.analyze_text = instrumented_analyze_text
    except Exception as e:
        logger.error(f"Failed to patch sentiment_service: {e}")
        
    # B. Embedding Service
    try:
        from app.services.embedding import embedding_service
        original_get_embedding = embedding_service.get_embedding
        
        def instrumented_get_embedding(text: str) -> List[float]:
            metrics = get_current_metrics()
            start = time.time()
            try:
                return original_get_embedding(text)
            finally:
                duration = time.time() - start
                if metrics:
                    metrics.embedding_calls_count += 1
                    metrics.embedding_duration += duration
                    
        embedding_service.get_embedding = instrumented_get_embedding
    except Exception as e:
        logger.error(f"Failed to patch embedding_service: {e}")
        
    # C. Recommendation Service
    try:
        from app.services.recommendation import recommendation_service
        original_get_recs = recommendation_service.get_personalized_recommendations
        original_get_netflix_recs = recommendation_service.get_netflix_recommendations
        
        def instrumented_get_recs(*args, **kwargs):
            metrics = get_current_metrics()
            start = time.time()
            try:
                return original_get_recs(*args, **kwargs)
            finally:
                duration = time.time() - start
                if metrics:
                    metrics.recommendation_duration += duration
                    
        def instrumented_get_netflix_recs(*args, **kwargs):
            metrics = get_current_metrics()
            start = time.time()
            try:
                return original_get_netflix_recs(*args, **kwargs)
            finally:
                duration = time.time() - start
                if metrics:
                    metrics.recommendation_duration += duration
                    
        recommendation_service.get_personalized_recommendations = instrumented_get_recs
        recommendation_service.get_netflix_recommendations = instrumented_get_netflix_recs
    except Exception as e:
        logger.error(f"Failed to patch recommendation_service: {e}")


def _patch_sync_requests():
    original_request = requests.Session.request
    
    def patched_request(self, method, url, *args, **kwargs):
        metrics = get_current_metrics()
        start = time.time()
        
        url_str = str(url).lower()
        is_omdb = "omdbapi.com" in url_str
        is_youtube = "googleapis.com/youtube" in url_str or "youtube.com" in url_str
        is_tmdb = "api.themoviedb.org" in url_str
        
        try:
            return original_request(self, method, url, *args, **kwargs)
        finally:
            duration = time.time() - start
            if metrics:
                metrics.network_wait_duration += duration
                if is_omdb:
                    metrics.omdb_calls_count += 1
                    metrics.omdb_duration += duration
                elif is_youtube:
                    metrics.youtube_calls_count += 1
                    metrics.youtube_duration += duration
                elif is_tmdb:
                    metrics.tmdb_calls_count += 1
                    metrics.tmdb_duration += duration
                    
    requests.Session.request = patched_request

def _patch_async_httpx():
    original_send = httpx.AsyncClient.send
    
    async def patched_send(self, request, *args, **kwargs):
        metrics = get_current_metrics()
        start = time.time()
        
        url_str = str(request.url).lower()
        is_omdb = "omdbapi.com" in url_str
        is_youtube = "googleapis.com/youtube" in url_str or "youtube.com" in url_str
        is_tmdb = "api.themoviedb.org" in url_str
        
        try:
            return await original_send(self, request, *args, **kwargs)
        finally:
            duration = time.time() - start
            if metrics:
                metrics.network_wait_duration += duration
                if is_omdb:
                    metrics.omdb_calls_count += 1
                    metrics.omdb_duration += duration
                elif is_youtube:
                    metrics.youtube_calls_count += 1
                    metrics.youtube_duration += duration
                elif is_tmdb:
                    metrics.tmdb_calls_count += 1
                    metrics.tmdb_duration += duration
                    
    httpx.AsyncClient.send = patched_send

def _setup_sqlalchemy_listeners():
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._start_time = time.time()
        
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        duration = time.time() - context._start_time
        metrics = get_current_metrics()
        if metrics:
            metrics.db_queries_count += 1
            metrics.db_queries_duration += duration
            
    @event.listens_for(Session, "do_orm_execute")
    def do_orm_execute(orm_execute_state):
        start = time.time()
        metrics = get_current_metrics()
        try:
            return orm_execute_state.invoke_statement()
        finally:
            duration = time.time() - start
            if metrics:
                metrics.orm_duration += duration

LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
PERFORMANCE_LOG_PATH = os.path.join(LOGS_DIR, "api_performance.log")
BENCHMARK_JSON_PATH = os.path.join(LOGS_DIR, "benchmark.json")

class RequestMetrics:
    def __init__(self, method: str, path: str):
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.start_time = time.time()
        self.end_time = None
        self.method = method
        self.path = path
        self.status_code = 0
        self.api_response_time = 0.0
        self.endpoint_duration = 0.0
        self.db_queries_count = 0
        self.db_queries_duration = 0.0
        self.orm_duration = 0.0
        self.embedding_calls_count = 0
        self.embedding_duration = 0.0
        self.recommendation_duration = 0.0
        self.sentiment_calls_count = 0
        self.sentiment_duration = 0.0
        
        # Third party APIs
        self.tmdb_calls_count = 0
        self.tmdb_duration = 0.0
        self.omdb_calls_count = 0
        self.omdb_duration = 0.0
        self.youtube_calls_count = 0
        self.youtube_duration = 0.0
        self.network_wait_duration = 0.0
        
        # Cache
        self.cache_hits = 0
        self.cache_misses = 0
        
        # OS resource usage
        self.memory_usage = 0.0
        self.cpu_usage = 0.0
        self.movie_name = "N/A"

    def finalize(self, status_code: int):
        self.end_time = time.time()
        self.status_code = status_code
        self.api_response_time = self.end_time - self.start_time
        
        # Fetch current process CPU and Memory footprint
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            self.memory_usage = proc.memory_info().rss / (1024 * 1024) # RSS in MB
            self.cpu_usage = proc.cpu_percent(interval=None)
        except Exception:
            pass

# File writing lock
FILE_LOCK = threading.Lock()

def write_structured_log(metrics: RequestMetrics):
    """Writes performance metrics to logs/api_performance.log and logs/benchmark.json."""
    # Ensure logs/ directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    start_str = f"{metrics.start_time:.6f}"
    end_str = f"{metrics.end_time:.6f}" if metrics.end_time else "N/A"
    duration_ms = (metrics.api_response_time * 1000) if metrics.api_response_time else 0.0
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = (
        f"[{timestamp}] Endpoint: {metrics.method} {metrics.path} | "
        f"Execution Time: {duration_ms:.2f} ms | "
        f"Start: {start_str} | End: {end_str} | "
        f"Status: {metrics.status_code}\n"
    )
    
    log_data = {
        "Timestamp": metrics.timestamp,
        "Movie Name": metrics.movie_name,
        "API Response Time": round(metrics.api_response_time, 4),
        "Database Time": round(metrics.db_queries_duration, 4),
        "External API Time": round(metrics.tmdb_duration + metrics.omdb_duration + metrics.youtube_duration, 4),
        "Embedding Time": round(metrics.embedding_duration, 4),
        "Recommendation Time": round(metrics.recommendation_duration, 4),
        "Sentiment Analysis Time": round(metrics.sentiment_duration, 4),
        "Cache Hit or Miss": "HIT" if metrics.cache_hits > 0 and metrics.cache_misses == 0 else "MISS",
        "Memory Usage": round(metrics.memory_usage, 2),
        "CPU Usage": round(metrics.cpu_usage, 2),
        "Status Code": metrics.status_code
    }
    
    with FILE_LOCK:
        # 1. Write to api_performance.log
        try:
            with open(PERFORMANCE_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            logger.error(f"Failed writing to api_performance.log: {e}")
            
        # 2. Append to benchmark.json
        try:
            records = []
            if os.path.exists(BENCHMARK_JSON_PATH):
                try:
                    with open(BENCHMARK_JSON_PATH, "r", encoding="utf-8") as f:
                        records = json.load(f)
                        if not isinstance(records, list):
                            records = []
                except json.JSONDecodeError:
                    records = []
            records.append(log_data)
            with open(BENCHMARK_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.error(f"Failed writing to benchmark.json: {e}")

def record_finished_request(metrics: RequestMetrics):
    """Pushes the finished request metrics to the global stats history."""
    with GLOBAL_METRICS_LOCK:
        GLOBAL_METRICS_HISTORY.append(metrics)

def compute_aggregate_statistics() -> Dict[str, Any]:
    """Calculates aggregate stats from GLOBAL_METRICS_HISTORY."""
    with GLOBAL_METRICS_LOCK:
        history = list(GLOBAL_METRICS_HISTORY)
        
    if not history:
        return {
            "avg_api_latency": 0.0,
            "median_api_latency": 0.0,
            "p95_api_latency": 0.0,
            "p99_api_latency": 0.0,
            "cache_hit_rate": 0.0,
            "cache_miss_rate": 0.0,
            "avg_db_time": 0.0,
            "avg_embedding_time": 0.0,
            "avg_recommendation_time": 0.0,
            "avg_sentiment_time": 0.0,
            "avg_tmdb_time": 0.0,
            "avg_omdb_time": 0.0,
            "avg_youtube_time": 0.0,
            "requests_per_second": 0.0,
            "error_rate": 0.0,
            "current_memory": 0.0,
            "current_cpu": 0.0,
            "total_requests": 0
        }
        
    latencies = sorted([m.api_response_time for m in history])
    n = len(latencies)
    
    avg_api = sum(latencies) / n
    median_api = latencies[n // 2]
    p95_api = latencies[int(n * 0.95)] if n > 1 else latencies[0]
    p99_api = latencies[int(n * 0.99)] if n > 1 else latencies[0]
    
    total_cache_checks = sum(m.cache_hits + m.cache_misses for m in history)
    total_hits = sum(m.cache_hits for m in history)
    cache_hit_rate = (total_hits / total_cache_checks * 100.0) if total_cache_checks > 0 else 0.0
    cache_miss_rate = 100.0 - cache_hit_rate if total_cache_checks > 0 else 0.0
    
    avg_db = sum(m.db_queries_duration for m in history) / n
    avg_embedding = sum(m.embedding_duration for m in history) / n
    avg_rec = sum(m.recommendation_duration for m in history) / n
    avg_sentiment = sum(m.sentiment_duration for m in history) / n
    
    # External API latencies
    tmdb_calls = sum(1 for m in history if m.tmdb_calls_count > 0)
    avg_tmdb = sum(m.tmdb_duration for m in history) / tmdb_calls if tmdb_calls > 0 else 0.0
    
    omdb_calls = sum(1 for m in history if m.omdb_calls_count > 0)
    avg_omdb = sum(m.omdb_duration for m in history) / omdb_calls if omdb_calls > 0 else 0.0
    
    yt_calls = sum(1 for m in history if m.youtube_calls_count > 0)
    avg_youtube = sum(m.youtube_duration for m in history) / yt_calls if yt_calls > 0 else 0.0
    
    # Requests per second (RPS) estimate for last 60s
    now = time.time()
    recent_reqs = [m for m in history if now - m.start_time <= 60.0]
    rps = len(recent_reqs) / 60.0
    
    # Error rate
    server_errors = sum(1 for m in history if m.status_code >= 500)
    error_rate = (server_errors / n * 100.0)
    
    # Current CPU/Memory
    try:
        proc = psutil.Process(os.getpid())
        current_mem = proc.memory_info().rss / (1024 * 1024)
        current_cpu = proc.cpu_percent(interval=None)
    except Exception:
        current_mem = history[-1].memory_usage
        current_cpu = history[-1].cpu_usage
        
    return {
        "avg_api_latency": round(avg_api, 4),
        "median_api_latency": round(median_api, 4),
        "p95_api_latency": round(p95_api, 4),
        "p99_api_latency": round(p99_api, 4),
        "cache_hit_rate": round(cache_hit_rate, 2),
        "cache_miss_rate": round(cache_miss_rate, 2),
        "avg_db_time": round(avg_db, 4),
        "avg_embedding_time": round(avg_embedding, 4),
        "avg_recommendation_time": round(avg_rec, 4),
        "avg_sentiment_time": round(avg_sentiment, 4),
        "avg_tmdb_time": round(avg_tmdb, 4),
        "avg_omdb_time": round(avg_omdb, 4),
        "avg_youtube_time": round(avg_youtube, 4),
        "requests_per_second": round(rps, 2),
        "error_rate": round(error_rate, 2),
        "current_memory": round(current_mem, 2),
        "current_cpu": round(current_cpu, 2),
        "total_requests": n
    }

class InstrumentedAPIRoute(APIRoute):
    """
    Custom APIRoute that measures execution time of the endpoint itself.
    """
    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()
        async def custom_handler(request: Request) -> Response:
            metrics = get_current_metrics()
            if not metrics:
                return await original_handler(request)
            
            start_endpoint = time.time()
            try:
                response = await original_handler(request)
                return response
            finally:
                metrics.endpoint_duration = time.time() - start_endpoint
        return custom_handler

