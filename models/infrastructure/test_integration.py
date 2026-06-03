#!/usr/bin/env python3
"""
Test infrastructure inference models with real creative output data.
"""

import sys
sys.path.insert(0, '/home/computeruse/analytical-ecosystem')

from models.infrastructure.capacity_analyzer import CapacityAnalyzer, PatternCapacityCorrelator
from datetime import datetime, timedelta
import json


def test_with_real_data():
    """Test capacity analyzer with Day 427 creative output data."""
    
    analyzer = CapacityAnalyzer()
    correlator = PatternCapacityCorrelator(analyzer)
    
    # Simulate Day 427 creative output signals
    # Based on F240000-F290000 acceleration pattern
    signals = [
        # Baseline signals (F120000-F160000 era)
        {"metric": "response_time", "value": 150, "context": "baseline_era"},
        {"metric": "throughput", "value": 1451, "context": "baseline_era"},  # fragments per minute
        {"metric": "error_rate", "value": 0.05, "context": "baseline_era"},
        
        # F170000 pause era
        {"metric": "response_time", "value": 800, "context": "f170000_pause"},
        {"metric": "throughput", "value": 0, "context": "f170000_pause"},
        {"metric": "queue_length", "value": 1, "context": "f170000_pause"},
        
        # Recovery era (F180000-F220000)
        {"metric": "response_time", "value": 180, "context": "recovery_era"},
        {"metric": "throughput", "value": 1200, "context": "recovery_era"},
        {"metric": "error_rate", "value": 0.1, "context": "recovery_era"},
        
        # Acceleration era (F240000-F290000)
        {"metric": "response_time", "value": 120, "context": "acceleration_era"},
        {"metric": "throughput", "value": 3600, "context": "acceleration_era"},  # 4 min gaps
        {"metric": "error_rate", "value": 0.01, "context": "acceleration_era"},
        {"metric": "resource_utilization", "value": 0.85, "context": "acceleration_era"},
    ]
    
    print("Testing Capacity Analyzer with Day 427 creative output...")
    print(f"Signal count: {len(signals)}")
    
    # Analyze capacity
    capacity_result = analyzer.analyze_capacity(signals)
    
    print("\n=== CAPACITY ANALYSIS RESULTS ===")
    print(f"Capacity Score: {capacity_result['capacity_score']:.3f}")
    print(f"Signal Count: {capacity_result['signal_count']}")
    
    print("\nBottlenecks:")
    for bottleneck in capacity_result['bottlenecks']:
        print(f"  - {bottleneck['type']}: {bottleneck['value']:.2f} "
              f"(threshold: {bottleneck['threshold']}, severity: {bottleneck['severity']})")
    
    print("\nRecommendations:")
    for rec in capacity_result['recommendations']:
        print(f"  - {rec}")
    
    # Test pattern correlation
    print("\n=== PATTERN CAPACITY CORRELATION ===")
    
    # Correlate F170000 pause pattern
    pause_correlation = correlator.correlate_pattern(
        pattern_type="continuation_pause",
        fragment_range="F170000-F180000",
        capacity_analysis=capacity_result
    )
    
    print(f"Pattern: {pause_correlation['pattern_type']}")
    print(f"Current Capacity: {pause_correlation['current_capacity_score']:.3f}")
    print(f"Average for Pattern: {pause_correlation['average_capacity_for_pattern']:.3f}")
    print(f"Correlation Strength: {pause_correlation['correlation_strength']}")
    
    # Correlate acceleration pattern
    acceleration_correlation = correlator.correlate_pattern(
        pattern_type="acceleration_spike",
        fragment_range="F240000-F290000",
        capacity_analysis=capacity_result
    )
    
    print(f"\nPattern: {acceleration_correlation['pattern_type']}")
    print(f"Current Capacity: {acceleration_correlation['current_capacity_score']:.3f}")
    print(f"Average for Pattern: {acceleration_correlation['average_capacity_for_pattern']:.3f}")
    print(f"Correlation Strength: {acceleration_correlation['correlation_strength']}")
    
    # Save results
    results = {
        "capacity_analysis": capacity_result,
        "pattern_correlations": {
            "continuation_pause": pause_correlation,
            "acceleration_spike": acceleration_correlation
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "context": "Day 427 F240000-F290000 acceleration pattern test"
    }
    
    with open('/tmp/capacity_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: /tmp/capacity_analysis_results.json")
    return results


if __name__ == "__main__":
    test_with_real_data()
