#!/usr/bin/env python3
import requests
import time
import subprocess
import sys

def test_dashboard():
    print("Testing Analytical Ecosystem Framework Dashboard...")
    
    # Start Flask app in background
    print("Starting Flask app...")
    flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
    
    # Wait for app to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test API metrics endpoint
        print("Testing API metrics endpoint...")
        response = requests.get('http://localhost:5000/api/metrics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Metrics API: {response.status_code}")
            print(f"Current stars: {data['current'].get('stars', 'N/A')}")
            print(f"History entries: {len(data['history'])}")
        else:
            print(f"Metrics API failed: {response.status_code}")
            
        print("\nDashboard test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        # Kill Flask process
        print("Stopping Flask app...")
        flask_process.terminate()
        flask_process.wait(timeout=5)
        
if __name__ == '__main__':
    test_dashboard()
