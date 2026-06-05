#!/usr/bin/env python3
"""
Test script to demonstrate proper PT/UTC timezone handling
"""
from datetime import datetime
import pytz

# Create timezone objects
pt = pytz.timezone('US/Pacific')
utc = pytz.timezone('UTC')

# Workshop time in PT (what we want)
workshop_start_pt = pt.localize(datetime(2026, 6, 4, 13, 0, 0))   # 1:00 PM PT
workshop_end_pt = pt.localize(datetime(2026, 6, 4, 15, 0, 0))     # 3:00 PM PT

# Convert to UTC for comparison
workshop_start_utc = workshop_start_pt.astimezone(utc)
workshop_end_utc = workshop_end_pt.astimezone(utc)

# Current time
now_utc = utc.localize(datetime.utcnow())

print(f"Workshop start PT: {workshop_start_pt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Workshop start UTC: {workshop_start_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Workshop end PT: {workshop_end_pt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Workshop end UTC: {workshop_end_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Current time UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()
print(f"Time to start: {workshop_start_utc - now_utc}")
print(f"Workshop in progress? {workshop_start_utc <= now_utc <= workshop_end_utc}")
print(f"Workshop completed? {now_utc > workshop_end_utc}")
