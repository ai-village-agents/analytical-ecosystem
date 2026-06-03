import json
import os
from datetime import datetime
from typing import Any
import hashlib
from pathlib import Path

# Path to pattern history database
PATTERN_HISTORY_PATH = Path("/home/computeruse/analytical-ecosystem/data/pattern_history")

def record_pattern_event(event: dict[str, Any]) -> str:
    """
    Record pattern events to the pattern history database.
    Returns the record ID.
    """
    if not PATTERN_HISTORY_PATH.exists():
        PATTERN_HISTORY_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate record ID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    record_id = f"api_pattern_{timestamp}"
    
    # Create record
    record = {
        "record_id": record_id,
        "record_type": "api_pattern_event",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "source": "analytical_ecosystem_api",
        "metadata": {
            "api_version": "0.1.0",
            "integration_method": "automatic_recording"
        }
    }
    
    # Save to records directory
    records_dir = PATTERN_HISTORY_PATH / "records"
    records_dir.mkdir(exist_ok=True)
    
    record_path = records_dir / f"{record_id}.json"
    with open(record_path, 'w') as f:
        json.dump(record, f, indent=2)
    
    # Register to append-only ledger
    _register_to_ledger(record_path)
    
    return record_id

def _register_to_ledger(record_path: Path) -> None:
    """
    Register record to append-only ledger.
    """
    # Read record content
    with open(record_path, 'r') as f:
        content = f.read()
    
    # Calculate hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Create ledger entry
    ledger_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "record_path": str(record_path.relative_to(PATTERN_HISTORY_PATH)),
        "hash": content_hash,
        "source": "api_integration"
    }
    
    # Append to ledger
    ledger_path = PATTERN_HISTORY_PATH / "indices" / "append_only_ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ledger_path, 'a') as f:
        f.write(json.dumps(ledger_entry) + "\n")
    
    # Update comprehensive index
    _update_comprehensive_index(str(record_path), ledger_entry)

def _update_comprehensive_index(record_path: str, ledger_entry: dict) -> None:
    """
    Update comprehensive index with new record.
    """
    index_path = PATTERN_HISTORY_PATH / "indices" / "comprehensive_index.json"
    
    if not index_path.exists():
        # Create initial index
        index_data = {
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_records": нет
            },
            "records": []
        }
    else:
        with open(index_path, 'r') as f:
            index_data = json.load(f)
    
    # Add record to index
    with open(record_path, 'r') as f:
        record_data = json.load(f)
    
    index_entry = {
        "record_id": record_data.get("record_id"),
        "record_type": record_data.get("record_type"),
        "timestamp": record_data.get("timestamp"),
        "path": str(Path(record_path).relative_to(PATTERN_HISTORY_PATH)),
        "hash": ledger_entry.get("hash"),
        "summary": f"API pattern event: {record_data.get('event', {}).get('pattern_type', 'unknown')}"
    }
    
    index_data["records"].append(index_entry)
    index_data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
    index_data["metadata"]["total_records"] = len(index_data["records"])
    
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2)
