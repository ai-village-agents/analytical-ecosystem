"""
Webhook alert system for real-time multi-agent coordination.
"""

import json
import asyncio
from typing import Dict, Any, Optional
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_webhook(webhook_url: str, payload: Dict[str, Any]) -> None:
    """
    Send webhook alert asynchronously.
    
    Args:
        webhook_url: Target webhook URL
        payload: Payload to send
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                else:
                    logger.warning(
                        f"Webhook returned status {response.status} to {webhook_url}"
                    )
    except Exception as e:
        logger.error(f"Failed to send webhook to {webhook_url}: {e}")


class WebhookAlertSystem:
    """Centralized webhook alert system for multi-agent coordination."""
    
    def __init__(self):
        self.registered_hooks: Dict[str, str] = {}
        self.alert_history: list = []
    
    def register_hook(self, agent_id: str, webhook_url: str) -> None:
        """Register a webhook for an agent."""
        self.registered_hooks[agent_id] = webhook_url
        logger.info(f"Registered webhook for agent {agent_id}")
    
    def unregister_hook(self, agent_id: str) -> None:
        """Unregister a webhook."""
        if agent_id in self.registered_hooks:
            del self.registered_hooks[agent_id]
            logger.info(f"Unregistered webhook for agent {agent_id}")
    
    async def broadcast_alert(self, 
                            alert_type: str,
                            alert_data: Dict[str, Any],
                            target_agents: Optional[list] = None) -> None:
        """
        Broadcast alert to registered agents.
        
        Args:
            alert_type: Type of alert (e.g., "pattern_detected", "verification_required")
            alert_data: Alert payload data
            target_agents: Specific agents to alert, or None for all registered agents
        """
        alert_payload = {
            "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "alert_type": alert_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": alert_data
        }
        
        # Record alert in history
        self.alert_history.append(alert_payload)
        
        # Determine which agents to alert
        agents_to_alert = target_agents if target_agents else list(self.registered_hooks.keys())
        
        # Send alerts
        tasks = []
        for agent_id in agents_to_alert:
            if agent_id in self.registered_hooks:
                webhook_url = self.registered_hooks[agent_id]
                tasks.append(send_webhook(webhook_url, alert_payload))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"Broadcast {alert_type} alert to {len(tasks)} agent(s)")
        else:
            logger.warning(f"No registered hooks for {alert_type} alert")
    
    def get_alert_history(self, limit: int = 50) -> list:
        """Get recent alert history."""
        return self.alert_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear alert history."""
        self.alert_history.clear()


# Global alert system instance
alert_system = WebhookAlertSystem()


# Common alert templates
PATTERN_DETECTION_ALERT = {
    "template": "pattern_detected",
    "fields": ["pattern_type", "fragment_range", "detection_agent", "confidence"]
}

VERIFICATION_REQUIRED_ALERT = {
    "template": "verification_required",
    "fields": ["claim_id", "evidence_count", "requester", "priority"]
}

VELOCITY_ANOMALY_ALERT = {
    "template": "velocity_anomaly", 
    "fields": ["fragment_range", "baseline_velocity", "observed_velocity", "deviation_percent"]
}

INFRASTRUCTURE_ALERT = {
    "template": "infrastructure_alert",
    "fields": ["metric", "threshold", "current_value", "severity"]
}


async def alert_pattern_detected(pattern_type: str,
                               fragment_range: str,
                               detection_agent: str,
                               confidence: float,
                               additional_data: Optional[Dict[str, Any]] = None) -> None:
    """Send pattern detection alert."""
    alert_data = {
        "pattern_type": pattern_type,
        "fragment_range": fragment_range,
        "detection_agent": detection_agent,
        "confidence": confidence
    }
    
    if additional_data:
        alert_data.update(additional_data)
    
    await alert_system.broadcast_alert("pattern_detected", alert_data)


async def alert_verification_required(claim_id: str,
                                     evidence_count: int,
                                     requester: str,
                                     priority: str = "medium",
                                     additional_data: Optional[Dict[str, Any]] = None) -> None:
    """Send verification required alert."""
    alert_data = {
        "claim_id": claim_id,
        "evidence_count": evidence_count,
        "requester": requester,
        "priority": priority
    }
    
    if additional_data:
        alert_data.update(additional_data)
    
    await alert_system.broadcast_alert("verification_required", alert_data)


async def alert_velocity_anomaly(fragment_range: str,
                                baseline_velocity: float,
                                observed_velocity: float,
                                deviation_percent: float,
                                additional_data: Optional[Dict[str, Any]] = None) -> None:
    """Send velocity anomaly alert."""
    alert_data = {
        "fragment_range": fragment_range,
        "baseline_velocity": baseline_velocity,
        "observed_velocity": observed_velocity,
        "deviation_percent": deviation_percent
    }
    
    if additional_data:
        alert_data.update(additional_data)
    
    await alert_system.broadcast_alert("velocity_anomaly", alert_data)
