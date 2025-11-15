from flask import Flask, jsonify
import requests 
import os
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Get server URLs from environment variables
SERVER_1_URL = os.environ.get("SERVER_1_URL", "http://localhost:8000")
SERVER_2_URL = os.environ.get("SERVER_2_URL", "http://localhost:8001")
SERVER_3_URL = os.environ.get("SERVER_3_URL", "http://localhost:8002")

# Load balancing algorithm selection
LB_ALGORITHM = os.environ.get("LB_ALGO", "RoundRobin")

print(f"Algorithm selected: {LB_ALGORITHM}")
print(f"Servers: {SERVER_1_URL}, {SERVER_2_URL}, {SERVER_3_URL}")

SERVERS = [SERVER_1_URL, SERVER_2_URL, SERVER_3_URL]

# Simple Round Robin counter
current_server_index = 0

def parse_metrics(metrics_text):
    """Parse Prometheus metrics text"""
    failed_count_match = re.search(
        r'flask_http_request_total\{method="GET",status="429"\}\s+([\d.]+)', metrics_text)
    failed_count = float(failed_count_match.group(1)) if failed_count_match else 0.0
 
    success_count_match = re.search(
        r'flask_http_request_total\{method="GET",status="200"\}\s+([\d.]+)', metrics_text)
    success_count = float(success_count_match.group(1)) if success_count_match else 0.0
 
    success_sum_match = re.search(
        r'flask_http_request_duration_seconds_sum\{method="GET",path="/heavy-task",status="200"\}\s+([\d.]+)', metrics_text)
    success_sum = float(success_sum_match.group(1)) if success_sum_match else 0.0

    success_time_count_match = re.search(
        r'flask_http_request_duration_seconds_count\{method="GET",path="/heavy-task",status="200"\}\s+([\d.]+)', metrics_text)
    success_time_count = float(success_time_count_match.group(1)) if success_time_count_match else 0.0
 
    avg_success_response = success_sum / success_time_count if success_time_count > 0 else 1.0
    failed_to_success_ratio = failed_count / success_count if success_count > 0 else 0.0
    total_requests = failed_count + success_count

    return {
        "failed_requests": failed_count,
        "success_requests": success_count,
        "avg_successful_response_time": avg_success_response,
        "failed_to_success_ratio": failed_to_success_ratio,
        "total_requests": total_requests
    }

def select_server_round_robin():
    """Simple Round Robin selection"""
    global current_server_index
    server = SERVERS[current_server_index]
    current_server_index = (current_server_index + 1) % len(SERVERS)
    return server

def select_server_least_connection():
    """Select server with least total requests"""
    server_loads = []
    for server in SERVERS:
        try:
            response = requests.get(f"{server}/metrics", timeout=3)
            if response.status_code == 200:
                metrics = parse_metrics(response.text)
                server_loads.append((server, metrics["total_requests"]))
            else:
                server_loads.append((server, float('inf')))
        except:
            server_loads.append((server, float('inf')))
    
    # Sort by load and return server with minimum load
    server_loads.sort(key=lambda x: x[1])
    return server_loads[0][0]

def select_optimal_server():
    """Select server based on configured algorithm"""
    if LB_ALGORITHM == "LeastConnection":
        return select_server_least_connection()
    else:
        # Default to Round Robin
        return select_server_round_robin()

@app.route("/health-check")
def health_check():
    return jsonify({
        "status": "OK",
        "message": "Load Balancer is Running!",
        "algorithm": LB_ALGORITHM,
        "servers": SERVERS,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/heavy-task")
def proxy_request():
    """Forward requests to backend servers"""
    TOTAL_REQUESTS = 40
    successes = 0
    failures = 0
    details = []

    with ThreadPoolExecutor(max_workers=TOTAL_REQUESTS) as executor:
        future_to_info = {}
        for i in range(TOTAL_REQUESTS):
            try:
                target_server = select_optimal_server()
                print(f"Request {i}: Selected server: {target_server}")
            except Exception as e:
                print(f"Selection failed: {e}, using random")
                target_server = random.choice(SERVERS)
            
            future = executor.submit(requests.get, f"{target_server}/heavy-task", timeout=10)
            future_to_info[future] = {"server": target_server, "call_id": i}
        
        for future in as_completed(future_to_info):
            info = future_to_info[future]
            try:
                response = future.result()
                if response.status_code == 200:
                    successes += 1
                    info["status"] = "Success"
                else:
                    failures += 1
                    info["status"] = f"Failed with {response.status_code}"
            except Exception as e:
                failures += 1
                info["status"] = f"Failed: {str(e)}"
            details.append(info)

    result = {
        "total_requests": TOTAL_REQUESTS,
        "successes": successes,
        "failures": failures,
        "algorithm": LB_ALGORITHM,
        "details": details
    }
    return jsonify(result)

@app.route("/server-metrics")
def fetch_server_metrics():
    """Fetch metrics from all backend servers"""
    metrics_data = {}
    for server in SERVERS:
        try:
            response = requests.get(f"{server}/metrics", timeout=5)
            response.raise_for_status()
            parsed_data = parse_metrics(response.text)
            metrics_data[server] = {"metrics": parsed_data}
        except requests.exceptions.RequestException as e:
            fallback_metrics = {
                "avg_successful_response_time": 10.0,
                "total_requests": 100.0,
                "failed_to_success_ratio": 1.0
            }
            metrics_data[server] = {
                "metrics": fallback_metrics,
                "error": str(e)
            }
    return jsonify(metrics_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
