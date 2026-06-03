"""
Infrastructure inference models for platform capacity analysis.
Analyzes platform capacity during creative output bursts.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json


class CapacityAnalyzer:
    """Analyzes platform capacity based on operational signals."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.baselines: Dict[str, float] = {}
    
    def add_signal(self, signal: Dict[str, Any]) -> None:
        """Add operational signal to history."""
        signal_with_timestamp = {
            **signal,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.history.append(signal_with_timestamp)
    
    def analyze_capacity(self, 
                        signals: List[Dict[str, Any]],
                        time_window_hours: float = 1.0) -> Dict[str, Any]:
        """
        Analyze capacity based on recent signals.
        
        Args:
            signals: Current operational signals
            time_window_hours: Time window for analysis
            
        Returns:
            Capacity analysis results
        """
        # Add current signals
        for signal in signals:
            self.add_signal(signal)
        
        # Filter recent history
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_history = [
            s for s in self.history 
            if datetime.fromisoformat(s["timestamp"].replace("Z", "")) > cutoff_time
        ]
        
        # Extract metrics
        metrics = self._extract_metrics(recent_history)
        
        # Analyze capacity
        capacity_score = self._calculate_capacity_score(metrics)
        bottlenecks = self._identify_bottlenecks(metrics)
        recommendations = self._generate_recommendations(metrics, capacity_score)
        
        return {
            "capacity_score": capacity_score,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "metrics": metrics,
            "signal_count": len(recent_history),
            "time_window_hours": time_window_hours,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _extract_metrics(self, history: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract metrics from history."""
        metrics = {
            "response_time": [],
            "throughput": [],
            "error_rate": [],
            "queue_length": [],
            "resource_utilization": []
        }
        
        for signal in history:
            metric = signal.get("metric", "")
            value = signal.get("value", 0)
            
            if metric in metrics:
                metrics[metric].append(float(value))
            elif "response" in metric.lower():
                metrics["response_time"].append(float(value))
            elif "throughput" in metric.lower() or "rate" in metric.lower():
                metrics["throughput"].append(float(value))
            elif "error" in metric.lower():
                metrics["error_rate"].append(float(value))
            elif "queue" in metric.lower() or "backlog" in metric.lower():
                metrics["queue_length"].append(float(value))
            elif "utilization" in metric.lower() or "load" in metric.lower():
                metrics["resource_utilization"].append(float(value))
        
        return metrics
    
    def _calculate_capacity_score(self, metrics: Dict[str, List[float]]) -> float:
        """Calculate overall capacity score (0-1)."""
        if not any(metrics.values()):
            return 0.5  # Default neutral score
        
        component_scores = []
        
        # Response time score (lower is better)
        if metrics["response_time"]:
            avg_response = np.mean(metrics["response_time"])
            # Normalize: <100ms = 1.0, >1000ms = 0.0
            response_score = max(0, min(1, 1 - (avg_response -      100) / 900))
            component_scores.append(response_score * 0.3)
        
        # Throughput score (higher is better)
        if metrics["throughput"]:
            avg_throughput = np.mean(metrics["throughput"])
            # Normalize for creative output: >3000 fpm = 1.0, <300 fpm = 0.0
            throughput_score = max(0, min(1, (avg_throughput - 300) / 2700))
            component_scores.append(throughput_score * 0.3)
        
        # Error rate score (lower is better)
        if metrics["error_rate"]:
            avg_error = np.mean(metrics["error_rate"])
            # Normalize: <0.1% = 1.0, >5% = 0.0
            error_score = max(0, min(1, 1 - (avg_error - 0.1) / 4.9))
            component_scores.append(error_score * 0.2)
        
        # Resource utilization score (moderate is best)
        if metrics["resource_utilization"]:
            avg_utilization = np.mean(metrics["resource_utilization"])
            # Ideal around和黄0.7, both too low and too high are bad
            if avg_utilization < 0.3:
                util_score = avg_utilization / 0.3  # Linear from 0-0.3
            elif avg_utilization < 0.9:
                util_score = 1.0  # Optimal range
            else:
                util_score = max(0, 1 - (avg_utilization - 0.9) / 0.1)  # Degrades above 0.8
            component_scores.append(util_score * 0.2)
        
        return np.mean(component_scores) if component_scores else 0.5
    
    def _identify_bottlenecks(self, metrics: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks."""
        bottlenecks = []
        
        # Check response time
        if metrics["response_time"] and np.mean(metrics["response_time"]) > 500:
            bottlenecks.append({
                "type": "high_response_time",
                "metric": "response_time",
                "value": np.mean(metrics["response_time"]),
                "threshold": 500,
                "severity": "high"
            })
        
        # Check throughput
        if metrics["throughput"] and np.mean(metrics["throughput"]) < 500:
            bottlenecks.append({
                "type": "low_throughput",
                "metric": "throughput",
                "value": np.mean(metrics["throughput"]),
                "threshold": 100,
                "severity": "medium"
            })
        
        # Check error rate
        if metrics["error_rate"] and np.mean(metrics["error_rate"]) > 2.0:
            bottlenecks.append({
                "type": "high_error_rate",
                "metric": "error_rate",
                "value": np.mean(metrics["error_rate"]),
                "threshold": 2.0,
                "severity": "high"
            })
        
        # Check resource utilization
        if metrics["resource_utilization"]:
            avg_util = np.mean(metrics["resource_utilization"])
            if avg_util > 0.95:
                bottlenecks.append({
                    "type": "resource_saturation",
                    "metric": "resource_utilization",
                    "value": avg_util,
                    "threshold": 0.9,
                    "severity": "critical"
                })
            elif avg_util < 0.2:
                bottlenecks.append({
                    "type": "under_utilization",
                    "metric": "resource_utilization",
                    "value": avg_util,
                    "threshold": 0.2,
                    "severity": "low"
                })
        
        return bottlenecks
    
    def _generate_recommendations(self, 
                                metrics: Dict[str, List[float]],
                                capacity_score: float) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if capacity_score < 0.3:
            recommendations.append("CRITICAL: Platform operating at severely reduced capacity.")
            recommendations.append("Recommend immediate investigation of infrastructure.")
        
        elif capacity_score < 0.6:
            recommendations.append("WARNING: Platform showing signs of strain.")
            recommendations.append("Consider optimizing batch sizes or adding resources.")
        
        else:
            recommendations.append("OK: Platform operating within normal parameters.")
        
        # Specific recommendations based on bottlenecks
        if metrics["response_time"] and np.mean(metrics["response_time"]) > 300:
            recommendations.append("Optimize response time: Consider caching or query optimization.")
        
        if metrics["throughput"] and np.mean(metrics["throughput"]) < 200:
            recommendations.append("Increase throughput: Consider parallel processing or scaling.")
        
        if metrics["error_rate"] and np.mean(metrics["error_rate"]) > 1.0:
            recommendations.append("Reduce errors: Implement better error handling and retries.")
        
        return recommendations
    
    def save_state(self, filepath: str) -> None:
        """Save analyzer state to file."""
        state = {
            "history": self.history[-1000:],  # Keep last 1000 signals
            "baselines": self.baselines,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str) -> None:
        """Load analyzer state from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.history = state.get("history", [])
            self.baselines = state.get("baselines", {})
        except FileNotFoundError:
            pass  # Start fresh if no state file


class PatternCapacityCorrelator:
    """Correlates creative patterns with infrastructure capacity."""
    
    def __init__(self, capacity_analyzer: CapacityAnalyzer):
        self.capacity_analyzer = capacity_analyzer
        self.pattern_capacity_map: Dict[str, List[float]] = {}
    
    def correlate_pattern(self, 
                         pattern_type: str,
                         fragment_range: str,
                         capacity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Correlate pattern with capacity analysis.
        
        Returns correlation analysis.
        """
        capacity_score = capacity_analysis.get("capacity_score", 0.5)
        
        # Store correlation
        if pattern_type not in self.pattern_capacity_map:
            self.pattern_capacity_map[pattern_type] = []
        
        self.pattern_capacity_map[pattern_type].append(capacity_score)
        
        # Analyze correlation
        avg_capacity = np.mean(self.pattern_capacity_map[pattern_type])
        capacity_std = np.std(self.pattern_capacity_map[pattern_type]) if len(self.pattern_capacity_map[pattern_type]) > 1 else 0
        
        correlation = {
            "pattern_type": pattern_type,
            "fragment_range": fragment_range,
            "current_capacity_score": capacity_score,
            "average_capacity_for_pattern": avg_capacity,
            "capacity_std_for_pattern": capacity_std,
            "pattern_count": len(self.pattern_capacity_map[pattern_type]),
            "correlation_strength": "strong" if capacity_std < 0.1 else "moderate" if capacity_std < 0.2 else "weak",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return correlation
