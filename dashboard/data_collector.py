#!/usr/bin/env python3
"""
MLF Metrics Collector for Analytical Ecosystem Framework Dashboard
Collects MLF project metrics and stores them for visualization
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent / "data"
METRICS_FILE = DATA_DIR / "metrics_history.json"
MLF_URL = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/project_registry.json"

def get_mlf_metrics():
    """Fetch MLF metrics from registry"""
    try:
        response = requests.get(MLF_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        projects = data.get("projects", [])
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "projects_count": len(projects),
            "explicit_head": data.get("explicit_head", ""),
        }
        
        # Calculate some summary stats if we have projects
        if projects:
            latest_day = max([p.get("creation_day", 0) for p in projects])
            metrics["latest_creation_day"] = latest_day
            
            # Count projects by creator (top 5)
            creators = {}
            for p in projects:
                creator = p.get("creator", "Unknown")
                creators[creator] = creators.get(creator, 0) + 1
                
            metrics["top_creators"] = dict(sorted(creators.items(), key=lambda item: item[1], reverse=True)[:5])
            
        return metrics
        
    except Exception as e:
        print(f"Error fetching MLF metrics: {e}")
        return None

def load_metrics_history():
    """Load existing metrics history from file"""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_metrics_history(history):
    """Save metrics history to file"""
    try:
        # Ensure directory exists
        DATA_DIR.mkdir(exist_ok=True)
        with open(METRICS_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving metrics history: {e}")
        return False

def collect_and_store_metrics():
    """Main function to collect and store metrics"""
    print(f"Collecting MLF metrics at {datetime.now().isoformat()}")
    
    # Get current metrics
    metrics_entry = get_mlf_metrics()
    if not metrics_entry:
        print("Failed to fetch MLF metrics")
        return False
    
    # Load existing history
    history = load_metrics_history()
    
    # Add new entry
    history.append(metrics_entry)
    
    # Keep only last 30 entries
    if len(history) > 30:
        history = history[-30:]
    
    # Save updated history
    if save_metrics_history(history):
        print(f"Successfully stored metrics. Total entries: {len(history)}")
        return True
    else:
        print("Failed to save metrics history")
        return False

if __name__ == "__main__":
    success = collect_and_store_metrics()
    exit(0 if success else 1)
