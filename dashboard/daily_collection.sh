#!/bin/bash
cd /tmp/analytical-ecosystem/dashboard
python3 data_collector.py
echo "Metrics collected at $(date)" >> collection.log
