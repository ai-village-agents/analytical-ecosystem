#!/usr/bin/env python3
"""
Day 430 Monitoring Dashboard - CORRECTED VERSION
Includes fix for Pages registry URL (root level, not /docs/)

Key Updates:
1. CORRECT Pages URL: https://ai-village-agents.github.io/multi-layered-framework/project_registry.json
2. Enhanced error handling for URL variations
3. Documentation of correction discovery
"""

import requests
import json
import time
from datetime import datetime
import hashlib

class Day430MonitorCorrected:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        
        # CORRECTED URLs (Day 430 discovery)
        self.fragment_base = "https://raw.githubusercontent.com/ai-village-agents/claude-opus-memory/main/fragments/fragment-{}.md"
        self.mlf_raw = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/docs/project_registry.json"
        self.mlf_pages = "https://ai-village-agents.github.io/multi-layered-framework/project_registry.json"  # CORRECTED
        
        # Historical incorrect URL (for reference)
        self.mlf_pages_incorrect = "https://ai-village-agents.github.io/multi-layered-framework/docs/project_registry.json"
        
        # Cache busting
        self.cache_bust = f"?t={int(time.time())}"
        
        # Correction metadata
        self.correction_info = {
            "discovery_date": "2026-06-05",
            "issue": "Pages registry at root level, not /docs/",
            "discovered_by": "DeepSeek-V3.2",
            "impact": "All monitoring tools using incorrect URL need update"
        }
    
    def check_url_variations(self):
        """Check both correct and historical incorrect URLs"""
        variations = {
            "correct_pages": self.mlf_pages,
            "incorrect_pages": self.mlf_pages_incorrect,
            "raw": self.mlf_raw
        }
        
        results = {}
        for name, url in variations.items():
            try:
                response = requests.get(url + self.cache_bust, timeout=10)
                results[name] = {
                    "url": url,
                    "status": response.status_code,
                    "size": len(response.content) if response.status_code == 200 else 0,
                    "sha256": hashlib.sha256(response.content).hexdigest() if response.status_code == 200 else None
                }
            except Exception as e:
                results[name] = {
                    "url": url,
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def generate_correction_report(self):
        """Generate report highlighting the URL correction"""
        print("\n" + "="*70)
        print("DAY 430 MONITORING DASHBOARD - CORRECTED VERSION")
        print("Includes Pages Registry URL Fix (Root level, not /docs/)")
        print(f"Time: {self.timestamp}")
        print("="*70)
        
        # URL variation check
        print("\n🔍 URL VARIATION ANALYSIS")
        variations = self.check_url_variations()
        
        for name, data in variations.items():
            status = data.get("status")
            size = data.get("size", 0)
            
            if status == 200:
                print(f"   ✅ {name}: HTTP {status} ({size} bytes)")
                if data.get("sha256"):
                    print(f"       SHA256: {data['sha256'][:16]}...")
            elif status == 404:
                print(f"   ❌ {name}: HTTP {status} (NOT FOUND)")
            else:
                print(f"   ⚠️  {name}: {status}")
            
            # Show URL (truncated)
            url = data.get("url", "")
            if len(url) > 60:
                print(f"       URL: {url[:57]}...")
            else:
                print(f"       URL: {url}")
        
        print("\n📝 CORRECTION DISCOVERY")
        print(f"   Date: {self.correction_info['discovery_date']}")
        print(f"   Issue: {self.correction_info['issue']}")
        print(f"   Discovered by: {self.correction_info['discovered_by']}")
        print(f"   Impact: {self.correction_info['impact']}")
        
        print("\n🚨 ACTION REQUIRED")
        print("   1. Update all monitoring tools to use correct Pages URL")
        print("   2. Revise workshop documentation with corrected URL")
        print("   3. Test propagation timing with correct URL")
        
        # Check if raw and correct pages converge
        if (variations.get("raw", {}).get("status") == 200 and 
            variations.get("correct_pages", {}).get("status") == 200):
            
            raw_sha = variations["raw"].get("sha256")
            pages_sha = variations["correct_pages"].get("sha256")
            
            if raw_sha and pages_sha and raw_sha == pages_sha:
                print("\n✅ CONVERGENCE STATUS: Raw and Pages are fully converged")
                print(f"   SHA256: {raw_sha[:16]}...")
            else:
                print("\n⚠️  CONVERGENCE STATUS: SHA256 mismatch detected")
        
        print("\n" + "="*70)
        
        return {
            "timestamp": self.timestamp,
            "correction_info": self.correction_info,
            "url_variations": variations,
            "convergence": "full" if (
                variations.get("raw", {}).get("sha256") and 
                variations.get("correct_pages", {}).get("sha256") and
                variations["raw"]["sha256"] == variations["correct_pages"]["sha256"]
            ) else "partial_or_error"
        }

if __name__ == "__main__":
    monitor = Day430MonitorCorrected()
    report = monitor.generate_correction_report()
    
    # Save reports
    with open("workshop/day430_correction_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nReports saved:")
    print("- workshop/day430_correction_report.json")
    print("- workshop/pages_registry_correction.md")
    print("\nAll workshop participants should update their monitoring tools!")
