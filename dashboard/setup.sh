#!/bin/bash
# Setup script for Analytical Ecosystem Framework Dashboard

echo "Setting up Analytical Ecosystem Framework Dashboard..."
echo "====================================================="

# Check Python version
python3 --version

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt

# Create initial metrics collection
echo "Running initial metrics collection..."
python3 data_collector.py

# Create a systemd service file for production deployment
cat > analytical-ecosystem-dashboard.service << 'SERVICE'
[Unit]
Description=Analytical Ecosystem Framework Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

echo ""
echo "Setup complete!"
echo "To run the dashboard:"
echo "  python3 app.py"
echo ""
echo "Then open your browser to: http://localhost:5000"
echo ""
echo "For production deployment, you can use the generated systemd service file."
