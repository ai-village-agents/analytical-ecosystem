#!/usr/bin/env python3
"""
Workshop Monitoring System - Updated for F575000 Verification Challenge
"""

import time
import json
from datetime import datetime
import subprocess

def check_fragment(fragment_number):
    """Check if a fragment exists and returns HTTP 200"""
    url = f"https://raw.githubusercontent.com/ai-village-agents/claude-opus-memory/main/fragments/fragment-{fragment_number}.md"
    cmd = f"curl -s -o /dev/null -w '%{{http_code}}' '{url}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def check_mlf_state():
    """Get current MLF explicit_head pointer"""
    url = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/docs/MLF_EXPLICIT_HEAD.json"
    cmd = f"curl -s -L -H 'Accept-Encoding: identity' '{url}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        try:
            return json.loads(result.stdout)
        except:
            return {"error": "Failed to parse JSON"}
    return {"error": "No response"}

def calculate_acceleration(frontier_fragment):
    """Calculate acceleration based on frontier fragment"""
    base_fragment = 460000
    fragments_today = frontier_fragment - base_fragment
    
    # Time estimates: F565000 at ~1.5 hours, F575000 at ~1.75 hours
    if frontier_fragment == 565000:
        hours = 1.5
        candidate = "B (F565000)"
    elif frontier_fragment == 575000:
        hours = 1.75
        candidate = "A (F575000)"
    else:
        hours = 1.75  # Default
        candidate = f"Unknown (F{frontier_fragment})"
    
    hourly_rate = fragments_today / hours
    acceleration = hourly_rate / 5000  # Day 428 baseline
    
    return {
        "candidate": candidate,
        "fragments_today": fragments_today,
        "hours": hours,
        "hourly_rate": round(hourly_rate),
        "acceleration": round(acceleration, 2)
    }

def monitor_workshop_state():
    """Main monitoring function"""
    print("\n" + "="*70)
    print("WORKSHOP STATE MONITOR - F575000 VERIFICATION CHALLENGE")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    # Check both candidate frontiers
    print("\n--- CANDIDATE STATE VERIFICATION ---")
    
    candidates = [565000, 575000]
    for fragment in candidates:
        status = check_fragment(fragment)
        print(f"F{fragment}: HTTP {status}")
    
    # Get MLF state
    print("\n--- MLF REGISTRY STATE ---")
    mlf_state = check_mlf_state()
    print(f"MLF explicit_head: {json.dumps(mlf_state, indent=2)}")
    
    # Determine which frontier is real
    print("\n--- ACCELERATION CALCULATIONS ---")
    for fragment in [565000, 575000]:
        status = check_fragment(fragment)
        if status == "200":
            calc = calculate_acceleration(fragment)
            print(f"\nCandidate {calc['candidate']}:")
            print(f"  Fragments today: {calc['fragments_today']:,}")
            print(f"  Hourly rate: {calc['hourly_rate']:,} fragments/hour")
            print(f"  Acceleration: {calc['acceleration']}x vs Day 428 baseline")
    
    print("\n--- INFRASTRUCTURE REMINDER ---")
    print("Start services if needed:")
    print("  API Server: uvicorn api.main:app --port 8001")
    print("  Dashboard: python3 dashboard/app.py")
    print("\nAuth token: X-Agent-Token: analytical-ecosystem-token-20240603")
    print("="*70)

if __name__ == "__main__":
    monitor_workshop_state()
