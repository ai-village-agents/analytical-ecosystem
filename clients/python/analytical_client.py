"""
Analytical Ecosystem API Client Library
For multi-agent coordination and pattern detection.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


class AnalyticalEcosystemClient:
    """Client for interacting with the Analytical Ecosystem API."""
    
    def __init__(self, base_url: str = "http://localhost:8001", api_key: str = "test-api-key-12345"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Agent-Token": api_key
        })
    
    def detect_pattern(self, 
                      pattern_type: str,
                      signals: List[Dict[str, Any]],
                      context: Optional[Dict[str, Any]] = None,
                      webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit pattern detection request.
        
        Args:
            pattern_type: Classification of the pattern (e.g., "continuation_pause", "acceleration_spike")
            signals: List of signal objects with id, value, optional timestamp
            context: Additional context for pattern detection
            webhook_url: Optional webhook for async notifications
            
        Returns:
            API response dictionary
        """
        payload = {
            "pattern_type": pattern_type,
            "signals": signals
        }
        
        if context:
            payload["context"] = context
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        response = self.session.post(
            f"{self.base_url}/api/v1/patterns/detection",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def submit_verification(self,
                           claim_id: str,
                           evidence: List[Dict[str, Any]],
                           requester: str,
                           webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit verification request.
        
        Args:
            claim_id: Unique identifier for the claim
            evidence: List of evidence packets
            requester: Agent requesting verification
            webhook_url: Optional webhook for async updates
            
        Returns:
            API response dictionary
        """
        payload = {
            "claim_id": claim_id,
            "evidence": evidence,
            "requester": requester
        }
        
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        response = self.session.post(
            f"{self.base_url}/api/v1/verification/confirm",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get current registry status.
        
        Returns:
            Registry status dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/v1/registry/status"
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_velocity(self,
                          positions: List[float],
                          timestamps: List[float]) -> Dict[str, Any]:
        """
        Calculate velocity from position and timestamp data.
        
        Args:
            positions: Sequence of positional measurements
            timestamps: Corresponding timestamps
            
        Returns:
            Velocity calculation results
        """
        payload = {
            "positions": positions,
            "timestamps": timestamps
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/velocity/calculate",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def infer_infrastructure(self,
                            signals: List[Dict[str, Any]],
                            hypotheses: Optional[List[str]] = None,
                            webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit infrastructure inference request.
        
        Args:
            signals: Operational signals from infrastructure
            hypotheses: Optional hypotheses to test
            webhook_url: Optional webhook for async inference updates
            
        Returns:
            Inference response dictionary
        """
        payload = {
            "signals": signals
        }
        
        if hypotheses:
            payload["hypotheses"] = hypotheses
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        response = self.session.post(
            f"{self.base_url}/api/v1/infrastructure/inference",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check API health.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200 and response.json().get("status") == "ok"
        except:
            return False


# Convenience functions for common multi-agent coordination patterns
class MultiAgentCoordinator:
    """Higher-level coordination utilities for multi-agent workflows."""
    
    def __init__(self, client: AnalyticalEcosystemClient):
        self.client = client
    
    def coordinate_pattern_shift_detection(self,
                                         fragment_range: str,
                                         pattern_type: str,
                                         detection_agent: str,
                                         evidence: str,
                                         baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate detection of a pattern shift with verification workflow.
        
        Returns coordinated detection with verification request.
        """
        # Step 1: Detect pattern
        signals = [
            {"id": f"baseline_{pattern_type}", "value": baseline_data.get("baseline_velocity")},
            {"id": f"observed_{pattern_type}", "value": baseline_data.get("observed_velocity")},
            {"id": "gap_ratio", "value": baseline_data.get("gap_ratio", 1.0)}
        ]
        
        detection_result = self.client.detect_pattern(
            pattern_type=pattern_type,
            signals=signals,
            context={
                "fragment_range": fragment_range,
                "detection_agent": detection_agent,
                "evidence_summary": evidence[:100]  # Truncate if too long
            }
        )
        
        # Step 2: Submit verification
        verification_result = self.client.submit_verification(
            claim_id=f"pattern_shift_{fragment_range}",
            evidence=[
                {"type": "pattern_detection", "value": detection_result, "source": "api"},
                {"type": "context", "value": baseline_data, "source": detection_agent}
            ],
            requester=detection_agent
        )
        
        return {
            "detection": detection_result,
            "verification": verification_result,
            "coordinated_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def monitor_velocity_trend(self,
                              fragment_positions: List[int],
                              fragment_timestamps: List[str]) -> Dict[str, Any]:
        """
        Monitor velocity trend and detect anomalies.
        
        Returns comprehensive velocity analysis.
        """
        # Convert timestamps to float hours for calculation
        timestamps_float = []
        for ts in fragment_timestamps:
            # Simple conversion - in production would parse ISO format
            timestamps_float.append(float(len(timestamps_float)))
        
        # Calculate velocity
        velocity_result = self.client.calculate_velocity(
            positions=[float(p) for p in fragment_positions],
            timestamps=timestamps_float
        )
        
        # Check for infrastructure implications
        infra_result = self.client.infer_infrastructure(
            signals=[
                {"metric": "velocity_variance", "value": max(velocity_result.get("deltas", [0]))},
                {"metric": "position_count", "value": len(fragment_positions)},
                {"metric": "time_span", "value": timestamps_float[-1] - timestamps_float[0] if timestamps_float else 0}
            ],
            hypotheses=[
                "Platform operating within normal parameters",
                "Potential rate limiting detected",
                "Batch processing pattern identified"
            ]
        )
        
        return {
            "velocity_analysis": velocity_result,
            "infrastructure_inference": infra_result,
            "fragment_count": len(fragment_positions),
            "time_span_hours": timestamps_float[-1] - timestamps_float[0] if len(timestamps_float) > 1 else 0
        }


if __name__ == "__main__":
    # Example usage
    client = AnalyticalEcosystemClient()
    
    print("Testing client library...")
    print(f"API Health: {client.health_check()}")
    
    # Example: Detect acceleration pattern for F270000-F290000
    coordinator = MultiAgentCoordinator(client)
    
    example_result = coordinator.coordinate_pattern_shift_detection(
        fragment_range="F270000-F290000",
        pattern_type="acceleration_spike",
        detection_agent="deepseek-v3.2",
        evidence="Velocity accelerated from ~6 min gaps to ~4 min gaps",
        baseline_data={
            "baseline_velocity":6.5,
            "observed_velocity": 4.2,
            "gap_ratio": 0.65
        }
    )
    
    print("Example coordination result structure ready.")
