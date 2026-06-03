#!/usr/bin/env python3
"""
Validation and append-only registration utility for the pattern_history database.

Responsibilities:
- Validate JSON records against the shared schema.
- Enforce timestamp and provenance requirements.
- Guard append-only semantics via a ledger of file hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_PATH = Path(__file__).with_name("pattern_history_schema.json")
LEDGER_PATH = Path(__file__).parent / "indices" / "append_only_ledger.jsonl"

RECORD_DIRECTORIES = {
    "shift_record": "records",
    "velocity_baseline": "velocity_baselines",
    "multi_agent_log": "multi_agent_logs",
    "predictive_fragment": "predictive_catalog",
    "tca_record": "tca_database",
}


def load_schema() -> Dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_timestamp(value: str) -> datetime:
    cleaned = value
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone information.")
    return dt


def validate_provenance(provenance: Dict[str, Any]) -> None:
    required = ("source", "collected_by", "method")
    missing = [field for field in required if field not in provenance]
    if missing:
        raise ValueError(f"Missing provenance fields: {', '.join(missing)}")
    for field in required:
        if not isinstance(provenance[field], str) or not provenance[field].strip():
            raise ValueError(f"Provenance field '{field}' must be a non-empty string.")
    for optional in ("upstream_reference",):
        if optional in provenance and not isinstance(provenance[optional], str):
            raise ValueError(f"Provenance field '{optional}' must be a string when provided.")


def validate_against_schema(entry: Dict[str, Any], schema: Dict[str, Any]) -> None:
    required_keys = schema.get("required", [])
    missing = [key for key in required_keys if key not in entry]
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(missing)}")

    if entry.get("record_type") not in RECORD_DIRECTORIES:
        raise ValueError(f"Unsupported record_type: {entry.get('record_type')}")

    for key, value in entry.items():
        if key not in schema["properties"]:
            raise ValueError(f"Unexpected field '{key}' in record.")
        if key == "id":
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Field 'id' must be a non-empty string.")
        elif key == "timestamp":
            if not isinstance(value, str):
                raise ValueError("Field 'timestamp' must be a string.")
            normalize_timestamp(value)
        elif key == "provenance":
            if not isinstance(value, dict):
                raise ValueError("Field 'provenance' must be an object.")
            validate_provenance(value)
        elif key == "links":
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                raise ValueError("Field 'links' must be an array of strings.")
        elif key == "content":
            if not isinstance(value, dict):
                raise ValueError("Field 'content' must be an object.")
        elif key == "checksum":
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError("Field 'checksum' must be a 64-character hex string.")
        elif key == "version":
            if not isinstance(value, str):
                raise ValueError("Field 'version' must be a string.")


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_ledger() -> List[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    entries = []
    with LEDGER_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def find_ledger_entry(path: Path, ledger: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    absolute = str(path.resolve())
    for row in ledger:
        if row.get("path") == absolute:
            return row
    return None


def ensure_append_only(path: Path, digest: str, ledger: List[Dict[str, Any]]) -> None:
    existing = find_ledger_entry(path, ledger)
    if existing is None:
        return
    if existing.get("hash") != digest:
        raise ValueError(f"Immutability violation: {path} changed (ledger hash {existing.get('hash')}, current {digest}).")


def append_to_ledger(path: Path, digest: str, record: Dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "path": str(path.resolve()),
        "hash": digest,
        "record_type": record["record_type"],
        "id": record["id"],
        "timestamp": record["timestamp"],
        "registered_at": datetime.now().astimezone().isoformat(),
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def validate_file(path: Path, expected_type: Optional[str] = None, register: bool = False) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    schema = load_schema()
    record = parse_json(path)

    validate_against_schema(record, schema)

    if expected_type and record.get("record_type") != expected_type:
        raise ValueError(f"Record type mismatch: expected {expected_type}, found {record.get('record_type')}")

    record_type_dir = RECORD_DIRECTORIES[record["record_type"]]
    if record_type_dir not in path.parts:
        raise ValueError(f"Record path should include '{record_type_dir}' for type '{record['record_type']}'.")

    digest = hash_file(path)
    ledger = read_ledger()
    ensure_append_only(path, digest, ledger)

    if register and find_ledger_entry(path, ledger) is None:
        append_to_ledger(path, digest, record)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate pattern_history records and enforce append-only ledger.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a record without writing to the ledger.")
    validate_parser.add_argument("path", type=Path, help="Path to the JSON record.")
    validate_parser.add_argument("--record-type", choices=RECORD_DIRECTORIES.keys(), help="Expected record type.")

    register_parser = subparsers.add_parser("register", help="Validate and append to the ledger.")
    register_parser.add_argument("path", type=Path, help="Path to the JSON record.")
    register_parser.add_argument("--record-type", choices=RECORD_DIRECTORIES.keys(), help="Expected record type.")

    args = parser.parse_args(argv)

    try:
        validate_file(args.path, expected_type=getattr(args, "record_type", None), register=args.command == "register")
    except Exception as exc:  # pylint: disable=broad-except
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
