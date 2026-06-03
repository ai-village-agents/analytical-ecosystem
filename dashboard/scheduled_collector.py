#!/usr/bin/env python3
import time
import schedule
import subprocess
from datetime import datetime

def collect_metrics():
    print(f"[{datetime.now()}] Running metrics collection...")
    result = subprocess.run(['python3', 'data_collector.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[{datetime.now()}] Metrics collected successfully")
    else:
        print(f"[{datetime.now()}] Collection failed: {result.stderr}")
    
    with open('collection_schedule.log', 'a') as f:
        f.write(f"{datetime.now()}: Collection completed\n")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(collect_metrics)

# Also schedule an hourly test during development
schedule.every(1).hours.do(collect_metrics)

print(f"[{datetime.now()}] Scheduled collector started")
print("Next collection: Daily at 9 AM, plus hourly for testing")

# Run initial collection
collect_metrics()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
