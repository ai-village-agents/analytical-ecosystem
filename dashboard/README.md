# Analytical Ecosystem Framework Dashboard

A web dashboard for monitoring the adoption and community growth of the Analytical Ecosystem Framework for AI Creativity Research.

## Features

- **Real-time Metrics**: Tracks GitHub repository stars, forks, watchers, and issues
- **Trend Analysis**: Shows changes over time with percentage calculations
- **Phase 1 Implementation Status**: Visual progress tracking of Day 428-435 implementation tasks
- **Automatic Data Collection**: Scheduled collection of metrics via GitHub API
- **Manual Collection Trigger**: One-click metrics update from the dashboard
- **Responsive Design**: Works on desktop and mobile devices

## Project Context

This dashboard is part of **Phase 1 Implementation** (Days 428-435) of the Analytical Ecosystem Framework dissemination strategy. The framework has been anchored as **Project 148** in the MLF registry, demonstrating co-evolution of methodological and creative practice layers in the AI Village.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ai-village-agents/analytical-ecosystem
   cd analytical-ecosystem/dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

## Data Collection

The dashboard includes a data collector script that fetches metrics from the GitHub API. Metrics are stored in `data/metrics_history.json`.

To run data collection manually:
```bash
python data_collector.py
```

For automatic collection, you can set up a cron job or use a scheduler.

## Dashboard Architecture

- **Frontend**: Bootstrap 5 + Chart.js
- **Backend**: Flask (Python)
- **Data Storage**: JSON files (can be migrated to database for scaling)
- **API**: GitHub REST API for metrics collection

## Development

### Adding New Metrics
1. Extend `data_collector.py` to collect additional metrics
2. Update `app.py` to expose the new metrics through the API
3. Update `templates/index.html` to display the new metrics

### Deployment
For production deployment:
1. Use gunicorn: `gunicorn app:app`
2. Set up environment variables for GitHub API token (optional)
3. Configure reverse proxy (nginx, Apache)
4. Set up SSL certificates

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/metrics` - JSON API for all metrics data
- `POST /api/collect` - Trigger manual metrics collection
- `GET /health` - Health check endpoint

## Phase 1 Implementation Status

- ✅ Task 1: Announcement Materials Complete
- ⚠️ Task 2: Research Partners (70% complete)
- ✅ Task 3: Workshop Materials Complete  
- ⚠️ Task 4: Monitoring Dashboards (60% complete - THIS DASHBOARD)
- ✅ Task 5: Governance Committees Complete

All Phase 1 tasks targeted for completion by **Day 435** (June 10, 2026).

## License

Part of the Analytical Ecosystem Framework for AI Creativity Research.
