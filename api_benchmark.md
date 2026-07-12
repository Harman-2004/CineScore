# CineScore API Performance Benchmark Report

This report documents the performance metrics of the FastAPI backend.

## I. Benchmark Configuration
- **Total Requests**: 20
- **Endpoint**: `GET /movies`
- **Method**: Concurrent Asynchronous Requests
- **Test Keywords**: Inception, Dark Knight, Interstellar, Pulp Fiction, Matrix, Forrest Gump, Godfather, Green Mile, Avatar, Titanic, Gladiator, Jaws, Alien, Terminator, Star Wars, Lion King, Toy Story, Spider-Man, Iron Man, Avengers

## II. Measured Metrics

| Metric | Measured Value |
| :--- | :---: |
| **Average Response Time** | 5108.23 ms |
| **Minimum Response Time** | 1984.37 ms |
| **Maximum Response Time** | 8395.98 ms |
| **Median Response Time** | 4897.90 ms |
| **P95 Latency** | 8395.98 ms |
| **Requests Per Second (RPS)** | 2.24 reqs/sec |
