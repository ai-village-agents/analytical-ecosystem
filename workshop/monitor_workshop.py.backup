#!/usr/bin/env python3
"""
Real-time workshop monitoring dashboard
"""
import time
import json
import requests
from datetime import datetime, timedelta

def check_dashboard():
    """Check dashboard health"""
    try:
        resp = requests.get("http://localhost:5000/health", timeout=5)
        return resp.status_code == 200, resp.json().get("status", "unknown")
    except Exception as e:
        return False, f"Error: {e}"

def check_mlf():
    """Check MLF endpoint"""
    try:
        resp = requests.get("http://localhost:5000/api/mlf", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return True, {
                "projects": data.get("total_projects", "unknown"),
                "converged": data.get("converged", "unknown"),
                "framework": data.get("framework_project", {}).get("name", "unknown")
            }
        return False, f"Status: {resp.status_code}"
    except Exception as e:
        return False, f"Error: {e}"

def check_api_server():
    """Check API server health"""
    try:
        headers = {"X-Agent-Token": "analytical-ecosystem-token-20240603"}
        resp = requests.get("http://localhost:8001/health", headers=headers, timeout=5)
        return resp.status_code == 200, resp.json().get("status", "unknown")
    except Exception as e:
        return False, f"Error: {e}"

def monitor_workshop():
    """Main monitoring loop"""
    workshop_start = datetime.strptime("2026-06-04 13:00:00", "%Y-%m-%d %H:%M:%S")
    workshop_end = datetime.strptime("2026-06-04 15:00:00", "%Y-%m-%d %H:%M:%S")
    
    modules = [
        ("Environment Setup", "13:00", "13:15"),
        ("MLF Convergence", "13:15", "13:45"),
        ("Dashboard Testing", "13:45", "14:15"),
        ("API Server Testing", "14:15", "14:40"),
        ("Committee Materials", "14:40", "14:55"),
        ("Wrap-up", "14:55", "15:00")
    ]
    
    print("=" * 60)
    print("WORKSHOP DAY 429 - REAL-TIME MONITORING DASHBOARD")
    print("=" * 60)
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        print(f"\n[{current_time}] System Status:")
        
        # Check systems
        dash_ok, dash_status = check_dashboard()
        mlf_ok, mlf_data = check_mlf()
        api_ok, api_status = check_api_server()
        
        print(f"  Dashboard: {'✅' if dash_ok else '❌'} {dash_status}")
        if mlf_ok and isinstance(mlf_data, dict):
            print(f"  MLF: ✅ {mlf_data.get('projects', '?')} projects, converged={mlf_data.get('converged', '?')}")
        else:
            print(f"  MLF: {'✅' if mlf_ok else '❌'} {mlf_data}")
        print(f"  API Server: {'✅' if api_ok else '❌'} {api_status}")
        
        # Workshop timing
        if now < workshop_start:
            time_left = workshop_start - now
            print(f"\n  Workshop starts in: {str(time_left).split('.')[0]}")
        elif now > workshop_end:
            print(f"\n  Workshop completed at 15:00")
            break
        else:
            elapsed = now - workshop_start
            total_duration = workshop_end - workshop_start
            progress = (elapsed.total_seconds() / total_duration.total_seconds()) * 100
            
            print(f"\n  Workshop progress: {progress:.1f}% ({elapsed.total_seconds()/60:.1f} minutes elapsed)")
            
            # Current module
            current_module = None
            for module_name, start_str, end_str in modules:
                start_time = datetime.strptime(f"2026-06-04 {start_str}:00", "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(f"2026-06-04 {end_str}:00", "%Y-%m-%d %H:%M:%S")
                if start_time <= now < end_time:
                    current_module = module_name
                    module_elapsed = now - start_time
                    module_duration = end_time - start_time
                    module_progress = (module_elapsed.total_seconds() / module_duration.total_seconds()) * 100
                    print(f"  Current module: {module_name} ({module_progress:.1f}% complete)")
                    break
            
            if not current_module:
                print("  Between modules")
        
        print("-" * 60)
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    try:
        monitor_workshop()
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
