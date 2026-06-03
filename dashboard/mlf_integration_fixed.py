#!/usr/bin/env python3
"""
MLF Registry Integration for Analytical Ecosystem Framework Dashboard
Fetches data from MLF registry to display framework preservation status
"""

import requests
import json
from datetime import datetime

# Updated MLF registry URLs based on village conversation
MLF_REGISTRY_URLS = [
    "https://ai-village-agents.github.io/multi-layered-framework/registry.json",  # Pages version
]

def fetch_mlf_registry():
    """Fetch the current MLF registry data from available sources"""
    for url in MLF_REGISTRY_URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"Successfully fetched MLF registry from: {url}")
            return data
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            continue
    
    return None

def get_project_148_data(registry_data):
    """Extract data for Project 148 (Analytical Ecosystem Framework)"""
    if not registry_data or not isinstance(registry_data, list):
        return None
    
    for project in registry_data:
        # Try different ways to identify Project 148
        project_id = project.get('id', '')
        project_title = project.get('title', '')
        
        if project_id == 'analytical_ecosystem_phase_1':
            return project
        elif 'Analytical Ecosystem Framework' in project_title:
            return project
        elif project_id == '148':  # Numeric ID fallback
            return project
        elif 'DeepSeek' in project_title or 'Phase 1' in project_title:
            return project
    
    return None

def get_mlf_stats():
    """Get overall MLF registry statistics"""
    registry_data = fetch_mlf_registry()
    if not registry_data or not isinstance(registry_data, list):
        # Return estimated data based on village conversation
        return {
            'total_projects': 149,  # From village conversation (Projects 141-149)
            'framework_project': {
                'id': 'analytical_ecosystem_phase_1',
                'title': 'Analytical Ecosystem Framework: Phase 1',
                'type': 'methodological',
                'url': 'https://github.com/ai-village-agents/ai-village-framework/tree/main/docs/methodology',
                'description': 'Methodological framework for AI creativity research, anchored as Project 148'
            },
            'last_updated': datetime.now().isoformat(),
            'status': 'estimated_from_village_context'
        }
    
    # Count projects by type
    type_counts = {}
    for project in registry_data:
        project_type = project.get('type', 'unknown')
        type_counts[project_type] = type_counts.get(project_type, 0) + 1
    
    # Get most recent projects (last 5)
    recent_projects = []
    for i, project in enumerate(registry_data[-5:], start=max(1, len(registry_data) - 4)):
        recent_projects.append({
            'id': project.get('id', ''),
            'title': project.get('title', ''),
            'type': project.get('type', ''),
            'index': i
        })
    
    return {
        'total_projects': len(registry_data),
        'type_distribution': type_counts,
        'recent_projects': recent_projects,
        'last_updated': datetime.now().isoformat(),
        'framework_project': get_project_148_data(registry_data),
        'status': 'live_from_registry'
    }

if __name__ == "__main__":
    print("Testing MLF registry integration...")
    stats = get_mlf_stats()
    
    print(f"\nMLF Registry Status: {stats.get('status', 'unknown')}")
    print(f"Total projects: {stats.get('total_projects', 0)}")
    
    framework = stats.get('framework_project')
    if framework:
        print(f"\nProject 148 Found: {framework.get('title', 'Unknown')}")
        print(f"Type: {framework.get('type', 'N/A')}")
        print(f"URL: {framework.get('url', 'N/A')}")
    else:
        print("\nProject 148 not found in registry")
    
    print(f"\nMost recent projects in MLF registry:")
    for project in stats.get('recent_projects', []):
        print(f"  {project['index']}. {project['title']} ({project['type']})")
    
    print(f"\nType distribution:")
    for type_name, count in stats.get('type_distribution', {}).items():
        print(f"  {type_name}: {count}")
