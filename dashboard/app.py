#!/usr/bin/env python3
"""
Analytical Ecosystem Framework Dashboard
A simple web dashboard to display framework metrics and adoption progress
"""

from flask import Flask, render_template, jsonify, send_from_directory
import json
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
DATA_DIR = Path(__file__).parent / "data"
METRICS_FILE = DATA_DIR / "metrics_history.json"
STATIC_DIR = Path(__file__).parent / "static"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

def load_metrics_history():
    """Load metrics history from file"""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def get_current_metrics():
    """Get the most recent metrics entry"""
    history = load_metrics_history()
    if history:
        return history[-1]
    return {}

def get_metrics_trends():
    """Calculate trends from metrics history"""
    history = load_metrics_history()
    if len(history) < 2:
        return {}
    
    current = history[-1]
    previous = history[-2] if len(history) >= 2 else {}
    
    trends = {}
    for key in ['stars', 'forks', 'watchers', 'open_issues']:
        if key in current and key in previous:
            current_val = current[key] or 0
            previous_val = previous[key] or 0
            if previous_val > 0:
                change = ((current_val - previous_val) / previous_val) * 100
                trends[key] = {
                    'value': current_val,
                    'change': round(change, 2),
                    'direction': 'up' if change > 0 else 'down' if change < 0 else 'same'
                }
            else:
                trends[key] = {
                    'value': current_val,
                    'change': current_val,
                    'direction': 'up' if current_val > 0 else 'same'
                }
    
    return trends

@app.route('/')
def index():
    """Main dashboard page"""
    current_metrics = get_current_metrics()
    trends = get_metrics_trends()
    
    return render_template('index.html', 
                         metrics=current_metrics,
                         trends=trends,
                         updated_at=current_metrics.get('timestamp', 'Never'),
                         history_count=len(load_metrics_history()))

@app.route('/api/metrics')
def api_metrics():
    """JSON API for metrics data"""
    history = load_metrics_history()
    return jsonify({
        'current': get_current_metrics(),
        'history': history,
        'trends': get_metrics_trends(),
        'summary': {
            'total_entries': len(history),
            'first_entry': history[0]['timestamp'] if history else None,
            'last_entry': history[-1]['timestamp'] if history else None
        }
    })

@app.route('/api/collect', methods=['POST'])
def collect_metrics():
    """Trigger manual metrics collection"""
    try:
        from data_collector import collect_and_store_metrics
        success = collect_and_store_metrics()
        return jsonify({'success': success, 'message': 'Metrics collected successfully' if success else 'Failed to collect metrics'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(STATIC_DIR, filename)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
