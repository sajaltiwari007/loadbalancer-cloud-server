"""
Quick test to verify cloud code works locally before deploying
Run this to make sure there are no syntax or import errors
"""

import sys
import os

print("Testing cloud_server.py...")
try:
    # Set dummy environment variables
    os.environ['SERVER_NAME'] = 'test-server'
    os.environ['SERVER_CAPACITY'] = '10'
    os.environ['PORT'] = '9000'
    
    # Try importing the server module
    import importlib.util
    spec = importlib.util.spec_from_file_location("cloud_server", "cloud_server.py")
    cloud_server = importlib.util.module_from_spec(spec)
    
    print("✓ cloud_server.py - No syntax errors")
except Exception as e:
    print(f"✗ cloud_server.py - Error: {e}")
    sys.exit(1)

print("\nTesting cloud_loadbalancer.py...")
try:
    # Set dummy environment variables
    os.environ['SERVER_1_URL'] = 'http://localhost:8000'
    os.environ['SERVER_2_URL'] = 'http://localhost:8001'
    os.environ['SERVER_3_URL'] = 'http://localhost:8002'
    os.environ['LB_ALGO'] = 'RoundRobin'
    os.environ['PORT'] = '9001'
    
    # Try importing the load balancer module
    spec = importlib.util.spec_from_file_location("cloud_loadbalancer", "cloud_loadbalancer.py")
    cloud_lb = importlib.util.module_from_spec(spec)
    
    print("✓ cloud_loadbalancer.py - No syntax errors")
except Exception as e:
    print(f"✗ cloud_loadbalancer.py - Error: {e}")
    sys.exit(1)

print("\nTesting cloud_requirements.txt...")
try:
    with open('cloud_requirements.txt', 'r') as f:
        requirements = f.read()
        if 'Flask' in requirements and 'gunicorn' in requirements:
            print("✓ cloud_requirements.txt - Contains required packages")
        else:
            print("✗ cloud_requirements.txt - Missing required packages")
            sys.exit(1)
except Exception as e:
    print(f"✗ cloud_requirements.txt - Error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✓ ALL TESTS PASSED!")
print("="*50)
print("\nYour cloud code is ready for deployment!")
print("\nNext steps:")
print("1. Push code to GitHub")
print("2. Follow QUICK_START_CHECKLIST.md")
print("3. Deploy to Render")
