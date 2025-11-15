import time
import random
import os

from flask import Flask, jsonify, Response, request
from flask_limiter import Limiter  
from flask_limiter.util import get_remote_address    
 
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from prometheus_client import Counter, Histogram

from prometheus_flask_exporter import PrometheusMetrics 

app = Flask(__name__)

# Get server capacity from environment variable (different for each deployment)
SERVER_CAPACITY = int(os.environ.get("SERVER_CAPACITY", "10"))
SERVER_NAME = os.environ.get("SERVER_NAME", "server")

limiter = Limiter(
    get_remote_address, 
    app=app
)   

limiter.init_app(app)   
metrics = PrometheusMetrics(app)
 
# Histogram for Request Response Time
req_response_time = Histogram(
    "http_flask_req_resp_time",
    "Total time taken in request-response by different routes.",
    ["method", "route", "statusCode"],
    buckets=[1, 5, 10, 15, 20, 40, 80, 100, 200, 500]
)

# Counter for Total Requests
total_req_counter = Counter(
    "total_requests",
    "Total requests made to the server."
)
 
# Middleware to Track Request Time
@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    total_req_counter.inc()
    duration = time.time() - request.start_time

    req_response_time.labels(
        method=request.method,
        route=request.path,
        statusCode=response.status_code
    ).observe(duration)

    return response

def heavyOperation(): 
    """Simulate a heavy computation with a random delay"""
    delay = random.uniform(0.5, 2)
    time.sleep(delay)
    return "OK!!"

@app.route("/")
def index():
    return jsonify({
        "message": "Server is running!",
        "server_name": SERVER_NAME,
        "capacity": SERVER_CAPACITY
    })

@app.route("/heavy-task")
@limiter.limit(lambda: f"{SERVER_CAPACITY} per second")
def heavy_task():
    try:
        result = heavyOperation()
        return result
    except Exception as e:
        return str(e), 500

@app.route("/metrics")
def metrics_endpoint():
    try:
        metrics_data = generate_latest(REGISTRY)    
        return Response(metrics_data, mimetype=CONTENT_TYPE_LATEST)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
