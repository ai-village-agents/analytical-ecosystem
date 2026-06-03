#!/usr/bin/env python3
"""
GitHub Metrics Collector for Analytical Ecosystem Framework Dashboard
Collects repository metrics and stores them for visualization
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
REPO_OWNER = "ai-village-agents"
REPO_NAME = "analytical-ecosystem"
GITHUB_API_BASE = "https://api.github.com"
DATA_DIR = Path(__file__).parent
METRICS_FILE = DATA_DIR / "metrics_history.json"

# Token for authenticated requests (optional, for higher rate limits)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def get_repository_metrics():
    """Fetch repository metrics from GitHub API"""
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    url = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("watchers_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "subscribers": data.get("subscribers_count", 0),
            "size_kb": data.get("size", 0),
            "default_branch": data.get("default_branch", "main"),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "pushed_at": data.get("pushed_at", ""),
            "clone_url": data.get("clone_url", ""),
            "homepage": data.get("homepage", ""),
            "description": data.get("description", "")
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error fetching repository metrics: {e}")
        return None

def get_traffic_metrics():
    """Fetch traffic metrics (requires authentication with push access)"""
    # Traffic endpoints require repository owner or collaborator access
    # We'll implement this later when we have appropriate permissions
    return {
        "clones": None,
        "views": None,
        "referrers": None,
        "paths": None
    }

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
        with open(METRICS_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving metrics history: {e}")
        return False

def collect_and_store_metrics():
    """Main function to collect and store metrics"""
    print(f"Collecting metrics for {REPO_OWNER}/{REPO_NAME} at {datetime.now().isoformat()}")
    
    # Get current metrics
    repo_metrics = get_repository_metrics()
    if not repo_metrics:
        print("Failed to fetch repository metrics")
        return False
    
    # Get traffic metrics (placeholder - requires authentication)
    traffic_metrics = get_traffic_metrics()
    
    # Combine metrics
    metrics_entry = {
        **repo_metrics,
        "traffic": traffic_metrics
    }
    
    # Load existing history
    history = load_metrics_history()
    
    # Check if we already have an entry for today
    today = datetime.now().date().isoformat()
    if history:
        last_entry = history[-1]
        last_date = datetime.fromisoformat(last_entry["timestamp"]).date().isoformat()
        if last_date == today:
            print(f"Already collected metrics today ({today}), updating entry")
            history[-1] = metrics_entry
        else:
            history.append(metrics_entry)
    else:
        history.append(metrics_entry)
    
    # Keep only last 30 days
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
