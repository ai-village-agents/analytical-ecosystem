#!/bin/bash
# Schedule automatic metrics collection

echo "Setting up scheduled metrics collection..."
echo "This will add a cron job to collect metrics daily at 9 AM."

# Check if crontab already has our job
if ! crontab -l 2>/dev/null | grep -q "data_collector.py"; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 9 * * * cd $(pwd) && python3 data_collector.py >> $(pwd)/collection.log 2>&1") | crontab -
    echo "Cron job added for daily collection at 9 AM."
else
    echo "Cron job already exists."
fi

echo ""
echo "To run collection manually: python3 data_collector.py"
echo "Logs will be saved to: collection.log"
