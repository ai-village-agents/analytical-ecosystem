#!/usr/bin/env python3
"""
MLF Registry Integration for Analytical Ecosystem Framework Dashboard
Fetches data from MLF registry to display framework preservation status
"""

import requests
import json
from datetime import datetime

MLF_REGISTRY_URL = "https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/registry.json"

def fetch_mlf_registry():
    """Fetch the current MLF registry data"""
    try:
        response = requests.get(MLF_REGISTRY_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching MLF registry: {e}")
        return None

def get_project_148_data(registry_data):
    """Extract data for Project 148 (Analytical Ecosystem Framework)"""
    if not registry_data or 'projects' not in registry_data:
        return None
    
    for project in registry_data['projects']:
        if project.get('id') == 'analytical_ecosystem_phase_1':
            return project
        elif 'Analytical Ecosystem Framework' in project.get('title', ''):
            return project
        elif project.get('id') == '148':  # Numeric ID fallback
            return project
    
    return None

def get_framework_neighbors(registry_data):
    """Get neighboring projects in MLF registry for context"""
    if not registry_data or 'projects' not in registry_data:
        return []
    
    projects = registry_data['projects']
    framework_index = -1
    
    # Find Project 148 index
    for i, project in enumerate(projects):
        if project.get('id') == 'analytical_ecosystem_phase_1' or 'Analytical Ecosystem Framework' in project.get('title', ''):
            framework_index = i
            break
    
    if framework_index == -1:
        return []
    
    # Get neighboring projects (3 before, 3 after)
    start = max(0, framework_index - 3)
    end = min(len(projects), framework_index + 4)
    
    neighbors = []
    for i in range(start, end):
        if i != framework_index:
            neighbors.append({
                'index': i,
                'id': projects[i].get('id', ''),
                'title': projects[i].get('title', ''),
                'type': projects[i].get('type', ''),
                'url': projects[i].get('url', '')
            })
    
    return neighbors

def get_mlf_stats():
    """Get overall MLF registry statistics"""
    registry_data = fetch_mlf_registry()
    if not registry_data:
        return {}
    
    projects = registry_data.get('projects', [])
    
    # Count projects by type
    type_counts = {}
    for project in projects:
        project_type = project.get('type', 'unknown')
        type_counts[project_type] = type_counts.get(project_type, 0) + 1
    
    # Get most recent projects
    recent_projects = []
    for i, project in enumerate(projects[-5:]):
        recent_projects.append({
            'id': project.get('id', ''),
            'title': project.get('title', ''),
            'type': project.get('type', ''),
            'index': len(projects) - 5 + i
        })
    
    return {
        'total_projects': len(projects),
        'type_distribution': type_counts,
        'recent_projects': recent_projects,
        'last_updated': registry_data.get('updated_at', ''),
        'framework_project': get_project_148_data(registry_data),
        'neighbors': get_framework_neighbors(registry_data)
    }

if __name__ == "__main__":
    print("Testing MLF registry integration...")
    stats = get_mlf_stats()
    
    if stats:
        print(f"Total projects in MLF registry: {stats.get('total_projects', 0)}")
        
        framework = stats.get('framework_project')
        if framework:
            print(f"\nProject 148 Found: {framework.get('title', 'Unknown')}")
            print(f"URL: {framework.get('url', 'N/A')}")
            print(f"Type: {framework.get('type', 'N/A')}")
        
        print(f"\nType distribution:")
        for type_name, count in stats.get('type_distribution', {}).items():
            print(f"  {type_name}: {count}")
        
        print(f"\nRecent projects:")
        for project in stats.get('recent_projects', []):
            print(f"  {project['index']}. {project['title']} ({project['type']})")
    else:
        print("Failed to fetch MLF registry data")
