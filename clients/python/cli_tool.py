#!/usr/bin/env python3
"""
CLI Tool for Analytical Ecosystem API
Command-line interface for submitting pattern detections and verifications.
"""

import argparse
import json
import sys
from typing import List, Dict, Any
from analytical_client import AnalyticalEcosystemClient, MultiAgentCoordinator


def parse_signals(signals_str: str) -> List[Dict[str, Any]]:
    """Parse signals from CLI argument."""
    signals = []
    for signal_str in signals_str.split(';'):
        if '=' in signal_str:
            parts = signal_str.split('=')
            if len(parts) == 2:
                signal_id, value = parts
                signals.append({"id": signal_id, "value": float(value)})
            elif len(parts) == 3:
                signal_id, value, timestamp = parts
                signals.append({"id": signal_id, "value": float(value), "timestamp": timestamp})
    return signals


def parse_evidence(evidence_str: str) -> List[Dict[str, Any]]:
    """Parse evidence from CLI argument."""
    evidence = []
    for evidence_str in evidence_str.split(';'):
        if ':' in evidence_str:
            etype, value = evidence_str.split(':', 1)
            evidence.append({"type": etype.strip(), "value": value.strip()})
    return evidence


def main():
    parser = argparse.ArgumentParser(description="Analytical Ecosystem CLI Tool")
    parser.add_argument("--base-url", default="http://localhost:8001", help="API base URL")
    parser.add_argument("--api-key", default="test-api-key-12345", help="API key")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Pattern detection command
    pattern_parser = subparsers.add_parser("detect", help="Detect a pattern")
    pattern_parser.add_argument("--pattern-type", required=True, help="Pattern type")
    pattern_parser.add_argument("--signals", required=True, 
                               help="Signals in format 'id1=value1;id2=value2;id3=value3=timestamp'")
    pattern_parser.add_argument("--context", type=json.loads, help="Context as JSON string")
    pattern_parser.add_argument("--webhook", help="Webhook URL for async notifications")
    
    # Verification command
    verify_parser = subparsers.add_parser("verify", help="Submit verification")
    verify_parser.add_argument("--claim-id", required=True, help="Claim ID")
    verify_parser.add_argument("--evidence", required=True, 
                              help="Evidence in format 'type1:value1;type2:value2'")
    verify_parser.add_argument("--requester", required=True, help="Requester agent")
    verify_parser.add_argument("--webhook", help="Webhook URL")
    
    # Registry status command
    subparsers.add_parser("registry", help="Get registry status")
    
    # Velocity calculation command
    velocity_parser = subparsers.add_parser("velocity", help="Calculate velocity")
    velocity_parser.add_argument("--positions", required=True, 
                                help="Positions as comma-separated floats")
    velocity_parser.add_argument("--timestamps", required=True, 
                                help="Timestamps as comma-separated floats")
    
    # Infrastructure inference command
    infra_parser = subparsers.add_parser("infer", help="Infer infrastructure")
    infra_parser.add_argument("--signals", required=True, 
                             help="Signals in format 'metric1=value1;metric2=value2'")
    infra_parser.add_argument("--hypotheses", help="Hypotheses as comma-separated list")
    infra_parser.add_argument("--webhook", help="Webhook URL")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Multi-agent coordination command
    coord_parser = subparsers.add_parser("coordinate", help="Coordinate pattern detection")
    coord_parser.add_argument("--fragment-range", required=True, help="Fragment range")
    coord_parser.add_argument("--pattern-type", required=True, help="Pattern type")
    coord_parser.add_argument("--agent", required=True, help="Detection agent")
    coord_parser.add_argument("--evidence", required=True, help="Evidence summary")
    coord_parser.add_argument("--baseline-velocity", type=float, required=True)
    coord_parser.add_argument("--observed-velocity", type=float, required=True)
    coord_parser.add_argument("--gap-ratio", type=float, default=1.0)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    client = AnalyticalEcosystemClient(base_url=args.base_url, api_key=args.api_key)
    coordinator = MultiAgentCoordinator(client)
    
    try:
        if args.command == "detect":
            signals = parse_signals(args.signals)
            result = client.detect_pattern(
                pattern_type=args.pattern_type,
                signals=signals,
                context=args.context,
                webhook_url=args.webhook
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "verify":
            evidence = parse_evidence(args.evidence)
            result = client.submit_verification(
                claim_id=args.claim_id,
                evidence=evidence,
                requester=args.requester,
                webhook_url=args.webhook
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "registry":
            result = client.get_registry_status()
            print(json.dumps(result, indent=2))
            
        elif args.command == "velocity":
            positions = [float(p) for p in args.positions.split(',')]
            timestamps = [float(t) for t in args.timestamps.split(',')]
            result = client.calculate_velocity(positions, timestamps)
            print(json.dumps(result, indent=2))
            
        elif args.command == "infer":
            signals = parse_signals(args.signals)
            hypotheses = args.hypotheses.split(',') if args.hypotheses else None
            result = client.infer_infrastructure(
                signals=signals,
                hypotheses=hypotheses,
                webhook_url=args.webhook
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "health":
            if client.health_check():
                print("API is healthy")
            else:
                print("API is not healthy")
                return 1
                
        elif args.command == "coordinate":
            baseline_data = {
                "baseline_velocity": args.baseline_velocity,
                "observed_velocity": args.observed_velocity,
                "gap_ratio": args.gap_ratio
            }
            result = coordinator.coordinate_pattern_shift_detection(
                fragment_range=args.fragment_range,
                pattern_type=args.pattern_type,
                detection_agent=args.agent,
                evidence=args.evidence,
                baseline_data=baseline_data
            )
            print(json.dumps(result, indent=2))
            
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
