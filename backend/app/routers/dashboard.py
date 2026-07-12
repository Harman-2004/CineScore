# dashboard.py
# Router module serving real-time performance analytics APIs and the developer status dashboard UI.

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.monitoring import compute_aggregate_statistics

router = APIRouter(tags=["Performance Monitoring"])

@router.get("/api/monitoring/stats")
async def get_monitoring_stats():
    """
    Returns aggregate performance analytics for the system.
    """
    return compute_aggregate_statistics()

@router.get("/monitoring/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """
    Renders a production-grade dark mode developer dashboard showing
    real-time charts and aggregate performance telemetry.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineScore Performance Telemetry Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #090d16 0%, #111827 100%);
            min-height: 100vh;
        }
        .mono {
            font-family: 'JetBrains Mono', monospace;
        }
        .glass {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.5);
        }
        .glow-cyan {
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
        }
        .glow-purple {
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
        }
    </style>
</head>
<body class="text-slate-100 p-6 lg:p-10">
    <div class="max-w-7xl mx-auto space-y-8">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-teal-400 to-purple-500 bg-clip-text text-transparent">
                    CineScore Performance Console
                </h1>
                <p class="text-slate-400 text-sm mt-1">Production-Grade Telemetry & Response Diagnostics</p>
            </div>
            <div class="flex items-center space-x-3">
                <span class="relative flex h-3.5 w-3.5">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500"></span>
                </span>
                <span class="text-sm font-semibold text-slate-300 mono">LIVE TELEMETRY ACTIVE</span>
            </div>
        </header>

        <!-- Stats Cards Grid -->
        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- API Latency Card -->
            <div class="glass rounded-2xl p-6 glow-cyan">
                <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Avg API Latency</p>
                <div class="flex items-baseline space-x-2 mt-2">
                    <span id="api-latency" class="text-3xl font-black text-cyan-400 mono">0.00</span>
                    <span class="text-sm text-slate-400 font-medium">seconds</span>
                </div>
                <div class="grid grid-cols-3 gap-1 mt-4 pt-4 border-t border-slate-800 text-[10px] text-slate-400 mono">
                    <div>Med: <span id="api-med" class="text-slate-200">0s</span></div>
                    <div>P95: <span id="api-p95" class="text-slate-200">0s</span></div>
                    <div>P99: <span id="api-p99" class="text-slate-200">0s</span></div>
                </div>
            </div>

            <!-- Throughput (RPS) Card -->
            <div class="glass rounded-2xl p-6 glow-cyan">
                <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Throughput</p>
                <div class="flex items-baseline space-x-2 mt-2">
                    <span id="throughput" class="text-3xl font-black text-cyan-400 mono">0.0</span>
                    <span class="text-sm text-slate-400 font-medium">reqs / sec</span>
                </div>
                <div class="text-[10px] text-slate-400 mt-4 pt-4 border-t border-slate-800 mono">
                    Total Requests Analyzed: <span id="total-reqs" class="text-slate-200">0</span>
                </div>
            </div>

            <!-- Cache Efficiency Card -->
            <div class="glass rounded-2xl p-6 glow-purple">
                <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Cache Efficiency</p>
                <div class="flex items-baseline space-x-2 mt-2">
                    <span id="cache-hit" class="text-3xl font-black text-purple-400 mono">0.0</span>
                    <span class="text-sm text-slate-400 font-medium">% hits</span>
                </div>
                <div class="text-[10px] text-slate-400 mt-4 pt-4 border-t border-slate-800 mono">
                    Miss Rate: <span id="cache-miss" class="text-slate-200">0%</span>
                </div>
            </div>

            <!-- Error and Reliability Card -->
            <div class="glass rounded-2xl p-6 glow-purple">
                <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Error Rate</p>
                <div class="flex items-baseline space-x-2 mt-2">
                    <span id="error-rate" class="text-3xl font-black text-rose-500 mono">0.0</span>
                    <span class="text-sm text-slate-400 font-medium">% fail</span>
                </div>
                <div class="text-[10px] text-slate-400 mt-4 pt-4 border-t border-slate-800 mono">
                    Server Status: <span id="server-status" class="text-emerald-400 font-bold">HEALTHY</span>
                </div>
            </div>
        </section>

        <!-- Main Charts Section -->
        <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Latency breakdown chart -->
            <div class="glass rounded-2xl p-6 lg:col-span-2 flex flex-col justify-between">
                <h3 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
                    <span class="h-2 w-2 rounded-full bg-cyan-400 mr-2"></span> Internal Execution Times (ms)
                </h3>
                <div class="h-64 relative">
                    <canvas id="componentsChart"></canvas>
                </div>
            </div>

            <!-- System resources -->
            <div class="glass rounded-2xl p-6 flex flex-col justify-between">
                <h3 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
                    <span class="h-2 w-2 rounded-full bg-purple-400 mr-2"></span> System Resources
                </h3>
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between text-sm font-semibold mb-2">
                            <span>CPU Usage</span>
                            <span id="cpu-percent" class="mono text-cyan-400">0%</span>
                        </div>
                        <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                            <div id="cpu-bar" class="bg-cyan-400 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>
                    <div>
                        <div class="flex justify-between text-sm font-semibold mb-2">
                            <span>Memory (RSS)</span>
                            <span id="memory-rss" class="mono text-purple-400">0 MB</span>
                        </div>
                        <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                            <div id="memory-bar" class="bg-purple-400 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div class="h-32 relative mt-4">
                    <canvas id="resourcesChart"></canvas>
                </div>
            </div>
        </section>

        <!-- External APIs & Detail Grid -->
        <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- External APIs Latency card -->
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
                    <span class="h-2 w-2 rounded-full bg-teal-400 mr-2"></span> External API Latency (seconds)
                </h3>
                <div class="space-y-4">
                    <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl">
                        <div class="flex items-center space-x-3">
                            <span class="text-xs font-bold px-2 py-1 rounded bg-yellow-500/20 text-yellow-500">TMDb</span>
                            <span class="text-sm font-semibold text-slate-300">The Movie Database API</span>
                        </div>
                        <span id="latency-tmdb" class="mono font-bold text-slate-100">0.000s</span>
                    </div>
                    <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl">
                        <div class="flex items-center space-x-3">
                            <span class="text-xs font-bold px-2 py-1 rounded bg-blue-500/20 text-blue-500">OMDb</span>
                            <span class="text-sm font-semibold text-slate-300">Open Movie Database API</span>
                        </div>
                        <span id="latency-omdb" class="mono font-bold text-slate-100">0.000s</span>
                    </div>
                    <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl">
                        <div class="flex items-center space-x-3">
                            <span class="text-xs font-bold px-2 py-1 rounded bg-rose-500/20 text-rose-500">YouTube</span>
                            <span class="text-sm font-semibold text-slate-300">YouTube Data API v3</span>
                        </div>
                        <span id="latency-youtube" class="mono font-bold text-slate-100">0.000s</span>
                    </div>
                </div>
            </div>

            <!-- Operations Averages card -->
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
                    <span class="h-2 w-2 rounded-full bg-purple-400 mr-2"></span> Average Duration Breakdown
                </h3>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="p-3 bg-slate-900/50 rounded-xl flex flex-col justify-between">
                        <span class="text-slate-400 text-xs">Database Engine Query</span>
                        <span id="avg-db" class="mono font-black text-cyan-400 mt-1">0.00ms</span>
                    </div>
                    <div class="p-3 bg-slate-900/50 rounded-xl flex flex-col justify-between">
                        <span class="text-slate-400 text-xs">Embedding Generation</span>
                        <span id="avg-embedding" class="mono font-black text-cyan-400 mt-1">0.00ms</span>
                    </div>
                    <div class="p-3 bg-slate-900/50 rounded-xl flex flex-col justify-between">
                        <span class="text-slate-400 text-xs">Recommendation Compilation</span>
                        <span id="avg-recommendation" class="mono font-black text-purple-400 mt-1">0.00ms</span>
                    </div>
                    <div class="p-3 bg-slate-900/50 rounded-xl flex flex-col justify-between">
                        <span class="text-slate-400 text-xs">Sentiment Analysis Inference</span>
                        <span id="avg-sentiment" class="mono font-black text-purple-400 mt-1">0.00ms</span>
                    </div>
                </div>
            </div>
        </section>

    </div>

    <!-- Chart rendering logic -->
    <script>
        // component charts setup
        const ctxComponents = document.getElementById('componentsChart').getContext('2d');
        const componentsChart = new Chart(ctxComponents, {
            type: 'bar',
            data: {
                labels: ['DB Query', 'HuggingFace Embeddings', 'Recommendation Engine', 'Sentiment Analysis'],
                datasets: [{
                    label: 'Avg Execution Latency (ms)',
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(6, 182, 212, 0.7)',
                        'rgba(20, 184, 166, 0.7)',
                        'rgba(168, 85, 247, 0.7)',
                        'rgba(236, 72, 153, 0.7)'
                    ],
                    borderColor: [
                        'rgba(6, 182, 212, 1)',
                        'rgba(20, 184, 166, 1)',
                        'rgba(168, 85, 247, 1)',
                        'rgba(236, 72, 153, 1)'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#cbd5e1', font: { family: 'Outfit', size: 11 } }
                    }
                }
            }
        });

        // resources line charts setup
        const ctxResources = document.getElementById('resourcesChart').getContext('2d');
        const resourcesChart = new Chart(ctxResources, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU (%)',
                        data: [],
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.05)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0
                    },
                    {
                        label: 'Memory (x10 MB)',
                        data: [],
                        borderColor: '#a855f7',
                        backgroundColor: 'rgba(168, 85, 247, 0.05)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        ticks: { color: '#94a3b8', font: { size: 9, family: 'JetBrains Mono' } }
                    },
                    x: {
                        display: false
                    }
                }
            }
        });

        // poll stats logic
        async function fetchAndUpdateStats() {
            try {
                const response = await fetch('/api/monitoring/stats');
                const data = await response.json();

                // update cards
                document.getElementById('api-latency').innerText = data.avg_api_latency.toFixed(3);
                document.getElementById('api-med').innerText = data.median_api_latency.toFixed(3) + 's';
                document.getElementById('api-p95').innerText = data.p95_api_latency.toFixed(3) + 's';
                document.getElementById('api-p99').innerText = data.p99_api_latency.toFixed(3) + 's';

                document.getElementById('throughput').innerText = data.requests_per_second.toFixed(1);
                document.getElementById('total-reqs').innerText = data.total_requests;

                document.getElementById('cache-hit').innerText = data.cache_hit_rate.toFixed(1);
                document.getElementById('cache-miss').innerText = data.cache_miss_rate.toFixed(1) + '%';

                document.getElementById('error-rate').innerText = data.error_rate.toFixed(1);
                const statusEl = document.getElementById('server-status');
                if (data.error_rate > 5) {
                    statusEl.innerText = 'DEGRADED';
                    statusEl.className = 'text-yellow-500 font-bold';
                } else if (data.error_rate > 15) {
                    statusEl.innerText = 'FAILING';
                    statusEl.className = 'text-rose-500 font-bold';
                } else {
                    statusEl.innerText = 'HEALTHY';
                    statusEl.className = 'text-emerald-400 font-bold';
                }

                // update averages breakdown
                document.getElementById('avg-db').innerText = (data.avg_db_time * 1000).toFixed(2) + 'ms';
                document.getElementById('avg-embedding').innerText = (data.avg_embedding_time * 1000).toFixed(2) + 'ms';
                document.getElementById('avg-recommendation').innerText = (data.avg_recommendation_time * 1000).toFixed(2) + 'ms';
                document.getElementById('avg-sentiment').innerText = (data.avg_sentiment_time * 1000).toFixed(2) + 'ms';

                // update external APIs
                document.getElementById('latency-tmdb').innerText = data.avg_tmdb_time.toFixed(3) + 's';
                document.getElementById('latency-omdb').innerText = data.avg_omdb_time.toFixed(3) + 's';
                document.getElementById('latency-youtube').innerText = data.avg_youtube_time.toFixed(3) + 's';

                // update components bar chart
                componentsChart.data.datasets[0].data = [
                    data.avg_db_time * 1000,
                    data.avg_embedding_time * 1000,
                    data.avg_recommendation_time * 1000,
                    data.avg_sentiment_time * 1000
                ];
                componentsChart.update();

                // update system sliders
                document.getElementById('cpu-percent').innerText = data.current_cpu.toFixed(0) + '%';
                document.getElementById('cpu-bar').style.width = data.current_cpu + '%';

                document.getElementById('memory-rss').innerText = data.current_memory.toFixed(1) + ' MB';
                // cap memory bar visual at 500MB max scaling
                const memBarWidth = Math.min(100, (data.current_memory / 500) * 100);
                document.getElementById('memory-bar').style.width = memBarWidth + '%';

                // update resources line chart
                const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                resourcesChart.data.labels.push(timeLabel);
                resourcesChart.data.datasets[0].data.push(data.current_cpu);
                resourcesChart.data.datasets[1].data.push(data.current_memory / 10); // scale memory to fit grid
                
                if (resourcesChart.data.labels.length > 20) {
                    resourcesChart.data.labels.shift();
                    resourcesChart.data.datasets[0].data.shift();
                    resourcesChart.data.datasets[1].data.shift();
                }
                resourcesChart.update();

            } catch (err) {
                console.error("Dashboard fetching stats failed: ", err);
            }
        }

        // initial execution and interval trigger (every 3 seconds)
        fetchAndUpdateStats();
        setInterval(fetchAndUpdateStats, 3000);
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
