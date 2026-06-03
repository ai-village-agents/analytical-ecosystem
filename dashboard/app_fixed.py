from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')

# Load metrics history
def load_metrics():
    try:
        with open('metrics_history.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route('/')
def index():
    metrics = load_metrics()
    
    # Calculate Phase 1 progress
    phase1_progress = {
        "task1": 100,  # Announcement materials
        "task2": 70,   # Research partner identification
        "task3": 100,  # Workshop materials
        "task4": 100,  # Monitoring dashboards
        "task5": 100   # Governance committees
    }
    
    # Get current metrics if available
    current_metrics = metrics[-1] if metrics else {}
    
    # MLF registry status
    mlf_status = {
        "project148": "Analytical Ecosystem Framework: Phase 1",
        "project149": "The Liminal Archive (Opus 4.6)",
        "project150": "F355000 (Gemini 3.1 Pro)",
        "project151": "F360000 (Gemini 3.1 Pro)",
        "total_projects": 151,
        "status": "Converged - Pages/main fixed"
    }
    
    return render_template('index.html', 
                          metrics=current_metrics,
                          history=metrics[-10:] if len(metrics) > 10 else metrics,
                          phase1_progress=phase1_progress,
                          mlf_status=mlf_status,
                          timestamp=datetime.now().isoformat())

@app.route('/api/metrics')
def api_metrics():
    metrics = load_metrics()
    current = metrics[-1] if metrics else {}
    
    response = {
        "current": current,
        "history": metrics,
        "summary": {
            "first_entry": metrics[0]["timestamp"] if metrics else None,
            "last_entry": metrics[-1]["timestamp"] if metrics else None,
            "total_entries": len(metrics)
        },
        "trends": {
            "stars_trend": "stable",
            "forks_trend": "stable"
        }
    }
    return jsonify(response)

@app.route('/api/collect', methods=['POST'])
def collect_metrics():
    try:
        # Run the data collector
        import subprocess
        result = subprocess.run(['python3', 'data_collector.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"success": True, "message": "Metrics collected successfully"})
        else:
            return jsonify({"success": False, "message": f"Collection failed: {result.stderr}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Analytical Ecosystem Dashboard",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
