"""
Simple script to test your cloud deployment
Replace the URLs with your actual Render URLs
"""

import requests
import json

# ===== REPLACE THESE WITH YOUR ACTUAL URLS =====
LOAD_BALANCER_URL = "https://your-loadbalancer.onrender.com"
SERVER_1_URL = "https://loadbalancer-server1.onrender.com"
SERVER_2_URL = "https://loadbalancer-server2.onrender.com"
SERVER_3_URL = "https://loadbalancer-server3.onrender.com"
# ===============================================

def test_server(url, name):
    """Test if a server is responding"""
    print(f"\n{'='*50}")
    print(f"Testing {name}: {url}")
    print('='*50)
    try:
        response = requests.get(f"{url}/", timeout=60)
        if response.status_code == 200:
            print(f"✓ {name} is ONLINE")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ {name} returned status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"✗ {name} timed out (might be cold starting, try again)")
        return False
    except Exception as e:
        print(f"✗ {name} failed: {e}")
        return False

def test_load_balancer_health():
    """Test load balancer health check"""
    print(f"\n{'='*50}")
    print(f"Testing Load Balancer Health Check")
    print('='*50)
    try:
        response = requests.get(f"{LOAD_BALANCER_URL}/health-check", timeout=60)
        if response.status_code == 200:
            print("✓ Load Balancer is ONLINE")
            data = response.json()
            print(f"Algorithm: {data.get('algorithm')}")
            print(f"Servers configured: {len(data.get('servers', []))}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_load_balancing():
    """Test actual load balancing"""
    print(f"\n{'='*50}")
    print(f"Testing Load Balancing (this will take ~30-60 seconds)")
    print('='*50)
    try:
        response = requests.get(f"{LOAD_BALANCER_URL}/heavy-task", timeout=120)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Load balancing test completed!")
            print(f"Total requests: {data.get('total_requests')}")
            print(f"Successes: {data.get('successes')}")
            print(f"Failures: {data.get('failures')}")
            print(f"Algorithm used: {data.get('algorithm')}")
            return True
        else:
            print(f"✗ Load balancing test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Load balancing test failed: {e}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing Server Metrics Collection")
    print('='*50)
    try:
        response = requests.get(f"{LOAD_BALANCER_URL}/server-metrics", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Metrics collected from {len(data)} servers")
            for server, metrics in data.items():
                if 'error' in metrics:
                    print(f"  ✗ {server}: {metrics['error']}")
                else:
                    print(f"  ✓ {server}: OK")
            return True
        else:
            print(f"✗ Metrics collection failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Metrics collection failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("CLOUD DEPLOYMENT TEST SUITE")
    print("="*50)
    
    # Check if URLs are configured
    if "your-loadbalancer" in LOAD_BALANCER_URL:
        print("\n⚠️  WARNING: Please update the URLs in this script first!")
        print("Edit test_cloud_deployment.py and replace the placeholder URLs")
        exit(1)
    
    results = []
    
    # Test individual servers
    results.append(("Server 1", test_server(SERVER_1_URL, "Server 1")))
    results.append(("Server 2", test_server(SERVER_2_URL, "Server 2")))
    results.append(("Server 3", test_server(SERVER_3_URL, "Server 3")))
    
    # Test load balancer
    results.append(("LB Health", test_load_balancer_health()))
    results.append(("LB Metrics", test_metrics()))
    results.append(("LB Load Balancing", test_load_balancing()))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your deployment is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
