# benchmark.py
import asyncio
import time
import subprocess
import os
import sys
import json
import statistics
import httpx

SERVER_URL = "http://127.0.0.1:8000"
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))

SEARCH_KEYWORDS = [
    "Inception", "Dark Knight", "Interstellar", "Pulp Fiction", "Matrix",
    "Forrest Gump", "Godfather", "Green Mile", "Avatar", "Titanic",
    "Gladiator", "Jaws", "Alien", "Terminator", "Star Wars", "Lion King",
    "Toy Story", "Spider-Man", "Iron Man", "Avengers"
]

def check_server_running() -> bool:
    try:
        response = httpx.get(SERVER_URL, timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False

def start_server() -> subprocess.Popen:
    print("[Benchmark] Starting uvicorn server...")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd, cwd=BACKEND_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def fetch_movie(client, kw, latencies):
    start = time.time()
    try:
        res = await client.get(f"{SERVER_URL}/movies", params={"query": kw}, timeout=30.0)
        duration = time.time() - start
        if res.status_code == 200:
            latencies.append(duration)
        else:
            print(f"[Benchmark] Request failed for {kw} with status: {res.status_code}")
    except Exception as e:
        print(f"[Benchmark] Request failed for {kw}: {e}")

async def run_benchmark():
    server_process = None
    if not check_server_running():
        server_process = start_server()
        # Wait for server to start
        for _ in range(30):
            await asyncio.sleep(1.0)
            if check_server_running():
                print("[Benchmark] Server started successfully.")
                break
        else:
            print("[Benchmark] ERROR: Server failed to start.")
            return
    else:
        print("[Benchmark] Server already running.")

    print(f"[Benchmark] Running exactly 20 movie searches concurrently...")
    latencies = []
    
    start_batch = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [fetch_movie(client, kw, latencies) for kw in SEARCH_KEYWORDS[:20]]
        await asyncio.gather(*tasks)
    end_batch = time.time()
    
    total_duration = end_batch - start_batch

    if not latencies:
        print("[Benchmark] ERROR: All 20 requests failed.")
        if server_process:
            server_process.terminate()
        return

    # Calculate metrics
    avg_lat = statistics.mean(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)
    med_lat = statistics.median(latencies)
    
    sorted_lat = sorted(latencies)
    p95_lat = sorted_lat[int(len(sorted_lat) * 0.95)] if len(sorted_lat) > 1 else sorted_lat[0]
    
    rps = len(latencies) / total_duration

    # Output json
    results = {
        "average_response_time_ms": round(avg_lat * 1000, 2),
        "minimum_response_time_ms": round(min_lat * 1000, 2),
        "maximum_response_time_ms": round(max_lat * 1000, 2),
        "median_response_time_ms": round(med_lat * 1000, 2),
        "p95_latency_ms": round(p95_lat * 1000, 2),
        "requests_per_second": round(rps, 2)
    }

    with open("api_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("[Benchmark] Created api_results.json successfully.")

    # Output markdown report
    markdown_report = f"""# CineScore API Performance Benchmark Report

This report documents the performance metrics of the FastAPI backend.

## I. Benchmark Configuration
- **Total Requests**: 20
- **Endpoint**: `GET /movies`
- **Method**: Concurrent Asynchronous Requests
- **Test Keywords**: {", ".join(SEARCH_KEYWORDS[:20])}

## II. Measured Metrics

| Metric | Measured Value |
| :--- | :---: |
| **Average Response Time** | {results["average_response_time_ms"]:.2f} ms |
| **Minimum Response Time** | {results["minimum_response_time_ms"]:.2f} ms |
| **Maximum Response Time** | {results["maximum_response_time_ms"]:.2f} ms |
| **Median Response Time** | {results["median_response_time_ms"]:.2f} ms |
| **P95 Latency** | {results["p95_latency_ms"]:.2f} ms |
| **Requests Per Second (RPS)** | {results["requests_per_second"]:.2f} reqs/sec |
"""

    with open("api_benchmark.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    print("[Benchmark] Created api_benchmark.md successfully.")

    # Tear down server if spawned by this script
    if server_process:
        print("[Benchmark] Tearing down background server process...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5.0)
        except Exception:
            server_process.kill()

    print("[Benchmark] Done.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
