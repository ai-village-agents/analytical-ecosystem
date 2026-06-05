#!/usr/bin/env python3
"""
Day 430 Monitoring Dashboard
Incorporating lessons from Day 429 Historic Real-time Scaling Workshop

Key Learnings Applied:
1. Direct fragment URL checks (bypass dashboard architecture issues)
2. MLF registry with schema detection (supports list-based schema)
3. Propagation timing measurement (Pages vs raw)
4. Configuration pattern awareness (patched/vanilla/direct)
"""

import requests
import json
import time
from datetime import datetime
import hashlib

class Day430Monitor:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        
        # URLs from workshop clarification
        self.fragment_base = "https://raw.githubusercontent.com/ai-village-agents/claude-opus-memory/main/fragments/fragment-{}.md"
        self.mlf_registry = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/docs/project_registry.json"
        self.mlf_pages = "https://ai-village-agents.github.io/multi-layered-framework/docs/project_registry.json"
        
        # Cache busting parameter from workshop findings
        self.cache_bust = f"?t={int(time.time())}"
        
    def check_fragment(self, fragment_id):
        """Check fragment availability with cache busting"""
        url = self.fragment_base.format(fragment_id) + self.cache_bust
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            size = len(response.content) if status == 200 else 0
            sha256 = hashlib.sha256(response.content).hexdigest() if status == 200 else None
            return {
                "fragment_id": fragment_id,
                "status": status,
                "size_bytes": size,
                "sha256": sha256,
                "url": url
            }
        except Exception as e:
            return {
                "fragment_id": fragment_id,
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    def check_mlf_registry(self):
        """Check MLF registry with schema detection"""
        results = {}
        
        # Check raw registry (workshop: most reliable)
        try:
            raw_response = requests.get(self.mlf_registry + self.cache_bust, timeout=10)
            if raw_response.status_code == 200:
                raw_data = raw_response.json()
                raw_size = len(raw_response.content)
                raw_sha256 = hashlib.sha256(raw_response.content).hexdigest()
                
                # Schema detection (workshop finding: list-based schema)
                if isinstance(raw_data, dict) and "projects" in raw_data:
                    if isinstance(raw_data["projects"], list):
                        schema_type = "list_based"
                        project_count = raw_data.get("total_projects", len(raw_data["projects"]))
                    else:
                        schema_type = "dict_based"
                        project_count = len(raw_data["projects"]) if isinstance(raw_data["projects"], dict) else 0
                else:
                    schema_type = "unknown"
                    project_count = 0
                
                results["raw"] = {
                    "status": 200,
                    "size_bytes": raw_size,
                    "sha256": raw_sha256,
                    "project_count": project_count,
                    "schema_type": schema_type
                }
            else:
                results["raw"] = {"status": raw_response.status_code}
        except Exception as e:
            results["raw"] = {"status": "error", "error": str(e)}
        
        # Check Pages registry (workshop: leads by 5-10 minutes)
        try:
            pages_response = requests.get(self.mlf_pages + self.cache_bust, timeout=10)
            if pages_response.status_code == 200:
                pages_size = len(pages_response.content)
                pages_sha256 = hashlib.sha256(pages_response.content).hexdigest()
                results["pages"] = {
                    "status": 200,
                    "size_bytes": pages_size,
                    "sha256": pages_sha256
                }
            else:
                results["pages"] = {"status": pages_response.status_code}
        except Exception as e:
            results["pages"] = {"status": "error", "error": str(e)}
        
        # Calculate propagation timing if both available
        if results.get("raw", {}).get("status") == 200 and results.get("pages", {}).get("status") == 200:
            if results["raw"]["sha256"] == results["pages"]["sha256"]:
                results["convergence"] = "fully_converged"
            else:
                results["convergence"] = "diverged"
        else:
            results["convergence"] = "incomplete_data"
        
        return results
    
    def check_frontier_range(self, start=650000, width=5):
        """Check a range of fragments to find frontier"""
        frontier = None
        checked = []
        
        for i in range(width):
            fragment_id = start + i * 1000
            result = self.check_fragment(fragment_id)
            checked.append(result)
            
            if result["status"] == 200:
                frontier = fragment_id
            elif frontier is not None and result["status"] == 404:
                # Found the boundary
                break
        
        return {
            "frontier": frontier,
            "checked_fragments": checked,
            "frontier_sha256": next((c["sha256"] for c in checked if c.get("sha256")), None)
        }
    
    def generate_report(self):
        """Generate comprehensive monitoring report"""
        print("\n" + "="*60)
        print("DAY 430 MONITORING DASHBOARD")
        print(f"Time: {self.timestamp}")
        print("Based on Day 429 Workshop Findings")
        print("="*60)
        
        # Check frontier
        print("\n1. FRAGMENT FRONTIER ANALYSIS")
        frontier_result = self.check_frontier_range(650000, 10)
        
        if frontier_result["frontier"]:
            print(f"   Current Frontier: F{frontier_result['frontier']}")
            print(f"   Frontier SHA256: {frontier_result['frontier_sha256']}")
            
            # Check next fragment
            next_fragment = frontier_result["frontier"] + 1000
            next_check = self.check_fragment(next_fragment)
            print(f"   Next Fragment (F{next_fragment}): HTTP {next_check['status']}")
            
            # Calculate fragments generated since F650000
            if frontier_result["frontier"] > 650000:
                fragments_since = (frontier_result["frontier"] - 650000) // 1000
                print(f"   Fragments since F650000: {fragments_since * 1000}")
        else:
            print("   No frontier found in checked range")
        
        # Check MLF registry
        print("\n2. MLF REGISTRY STATUS")
        mlf_result = self.check_mlf_registry()
        
        raw_status = mlf_result.get("raw", {})
        pages_status = mlf_result.get("pages", {})
        
        if raw_status.get("status") == 200:
            print(f"   Raw Registry: {raw_status.get('project_count', 'N/A')} projects")
            print(f"   Schema Type: {raw_status.get('schema_type', 'unknown')}")
            print(f"   SHA256: {raw_status.get('sha256', 'N/A')[:16]}...")
        else:
            print(f"   Raw Registry: HTTP {raw_status.get('status', 'error')}")
        
        if pages_status.get("status") == 200:
            print(f"   Pages Registry: {pages_status.get('size_bytes', 'N/A')} bytes")
            print(f"   SHA256: {pages_status.get('sha256', 'N/A')[:16]}...")
        else:
            print(f"   Pages Registry: HTTP {pages_status.get('status', 'error')}")
        
        print(f"   Convergence: {mlf_result.get('convergence', 'unknown')}")
        
        # Propagation timing assessment
        print("\n3. PROPAGATION ASSESSMENT")
        if raw_status.get("status") == 200 and pages_status.get("status") == 200:
            if mlf_result.get("convergence") == "fully_converged":
                print("   ✅ Pages and Raw are fully converged")
            else:
                print("   ⚠️  Pages and Raw show divergence")
                print("   Note: Workshop found Pages typically leads by 5-10 minutes")
        else:
            print("   ⚠️  Incomplete data for propagation assessment")
        
        # Configuration awareness
        print("\n4. CONFIGURATION AWARENESS")
        print("   Workshop-Identified Patterns:")
        print("   1. Patched Dashboard (Gemini 3.1 Pro): Custom /api/mlf endpoint")
        print("   2. Vanilla Dashboard: data_collector.py collects repo stats, not MLF")
        print("   3. Direct Checks (Recommended): Bypass dashboard, use raw URLs")
        print("   Current Mode: Direct URL checks (most reliable)")
        
        # Recommendations
        print("\n5. RECOMMENDATIONS FROM DAY 429 WORKSHOP")
        print("   • Use direct fragment/MLF URL checks for reliability")
        print("   • Implement schema detection for MLF registry parsing")
        print("   • Monitor propagation timing (Pages vs Raw)")
        print("   • Cache-bust with ?t= parameter for fresh data")
        print("   • Document configuration patterns clearly")
        
        print("\n" + "="*60)
        
        # Return structured data
        return {
            "timestamp": self.timestamp,
            "frontier": frontier_result,
            "mlf_registry": mlf_result,
            "configuration": "direct_url_checks",
            "workshop_lessons_applied": [
                "direct_fragment_checks",
                "mlf_schema_detection", 
                "propagation_monitoring",
                "cache_busting",
                "configuration_awareness"
            ]
        }

if __name__ == "__main__":
    monitor = Day430Monitor()
    report = monitor.generate_report()
    
    # Save report to file
    with open("workshop/day430_monitoring_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nReport saved to workshop/day430_monitoring_report.json")
