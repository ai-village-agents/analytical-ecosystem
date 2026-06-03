#!/usr/bin/env python3
"""
MLF Registry Integration for Analytical Ecosystem Framework Dashboard
Fetches data from MLF registry to display framework preservation status
"""

import requests
import json
from datetime import datetime

MLF_REGISTRY_URL = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/docs/project_registry.json"
MLF_EXPLICIT_HEAD_URL = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/MLF_EXPLICIT_HEAD.json"

def fetch_mlf_registry():
    """Fetch the current MLF registry data"""
    try:
        response = requests.get(MLF_REGISTRY_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching MLF registry: {e}")
        return None

def fetch_mlf_explicit_head():
    """Fetch the explicit head data for convergence checking"""
    try:
        response = requests.get(MLF_EXPLICIT_HEAD_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching MLF explicit head: {e}")
        return None

def get_mlf_stats():
    """Get overall MLF registry statistics and convergence status"""
    registry_data = fetch_mlf_registry()
    head_data = fetch_mlf_explicit_head()
    
    if not registry_data or not head_data:
        return {}
    
    projects = registry_data.get('projects', [])
    registry_count = len(projects)
    head_count = head_data.get('total_projects', 0)
    
    is_converged = (registry_count == head_count)
    
    # Get project 148 (index 147 in list if 1-indexed initially) or by ID
    framework_project = None
    for p in projects:
        if p.get('id') == 'analytical_ecosystem_phase_1':
            framework_project = p
            break
            
    if not framework_project and len(projects) >= 148:
        # Fallback to index if title matches
        if 'Analytical Ecosystem' in projects[147].get('title', '') or 'Analytical Ecosystem' in projects[147].get('name', ''):
            framework_project = projects[147]

    # Get most recent projects
    recent_projects = []
    for i, project in enumerate(projects[-5:]):
        recent_projects.append({
            'id': project.get('id', ''),
            'title': project.get('name', project.get('title', 'Unknown')),
            'type': project.get('type', ''),
            'index': len(projects) - 5 + i + 1
        })
    
    return {
        'total_projects': registry_count,
        'head_count': head_count,
        'is_converged': is_converged,
        'recent_projects': recent_projects,
        'last_updated': head_data.get('last_updated', ''),
        'framework_project': framework_project
    }

if __name__ == "__main__":
    print("Testing MLF registry integration...")
    stats = get_mlf_stats()
    
    if stats:
        print(f"Total projects in MLF registry: {stats.get('total_projects', 0)}")
        print(f"Total projects in MLF explicit head: {stats.get('head_count', 0)}")
        print(f"Convergence Status: {'Converged' if stats.get('is_converged') else 'Diverged'}")
        
        framework = stats.get('framework_project')
        if framework:
            print(f"\nProject 148 Found: {framework.get('name', framework.get('title', 'Unknown'))}")
            print(f"URL: {framework.get('url', 'N/A')}")
        
        print(f"\nRecent projects:")
        for project in stats.get('recent_projects', []):
            print(f"  {project['index']}. {project['title']} ({project['type']})")
    else:
        print("Failed to fetch MLF registry data")
