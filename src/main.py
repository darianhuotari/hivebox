"""Main FastAPI app"""
import time
import psutil

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY # pylint: disable=line-too-long

from endpoints import temperature, version

app = FastAPI()

# Custom metrics
REQUEST_COUNT = Counter('http_request_total', 'Total HTTP Requests', ['method', 'status', 'path'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'status', 'path']) # pylint: disable=line-too-long
REQUEST_IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP Requests in progress', ['method', 'path']) # pylint: disable=line-too-long

# System metrics
CPU_USAGE = Gauge('process_cpu_usage', 'Current CPU usage in percent')
MEMORY_USAGE = Gauge('process_memory_usage_bytes', 'Current memory usage in bytes')

def update_system_metrics():
    """Update system metrics when /metrics endpoint is called"""
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Middleware to monitor requests"""
    method = request.method
    path = request.url.path

    REQUEST_IN_PROGRESS.labels(method=method, path=path).inc()

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    status = response.status_code
    REQUEST_COUNT.labels(method=method, status=status, path=path).inc()
    REQUEST_LATENCY.labels(method=method, status=status, path=path).observe(duration)
    REQUEST_IN_PROGRESS.labels(method=method, path=path).dec()

    return response


@app.get("/")
async def root():
    """Temporary route"""
    return {"message": "Hello World"}


@app.get("/version")
async def get_version():
    """Get the current app version"""
    app_version = version.list_version()
    return {f"Version: {app_version}"}


@app.get("/temperature")
async def get_temperature():
    """Get the current average temperature"""
    avg, status = await temperature.avg_temperature()
    return {f"Average temperature (°C): {avg}", f"Status: {status}"}


@app.get("/metrics")
async def metrics():
    """Simple metrics endpoint"""
    update_system_metrics()
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
