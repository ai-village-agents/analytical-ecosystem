import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


INDEX_PATH = Path(__file__).with_name("comprehensive_index.json")


def load_index(path: Path = INDEX_PATH) -> Dict[str, Any]:
    """Load the comprehensive index from disk."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_record_map(index: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return a lookup map from record id to record metadata."""
    return {record["id"]: record for record in index.get("records", [])}


def search_by_dimension(index: Dict[str, Any], dimension: str, key: str) -> List[Dict[str, Any]]:
    """
    Resolve records using a pre-built search dimension (e.g., pattern_type, severity, agents_involved).
    """
    dim = index.get("search_indices", {}).get(dimension, {})
    ids = dim.get(key, [])
    record_map = get_record_map(index)
    return [record_map[rid] for rid in ids if rid in record_map]


def search_by_attribute(index: Dict[str, Any], attribute: str, value: Any) -> List[Dict[str, Any]]:
    """
    Filter records by an attribute within the record attributes block.
    Matches exact values; iterates across arrays when the attribute value is a list.
    """
    results: List[Dict[str, Any]] = []
    for record in index.get("records", []):
        attrs = record.get("attributes", {})
        if attribute not in attrs:
            continue
        attr_val = attrs[attribute]
        if attr_val == value:
            results.append(record)
        elif isinstance(attr_val, list) and value in attr_val:
            results.append(record)
    return results


def format_records(records: List[Dict[str, Any]]) -> str:
    lines = []
    for rec in records:
        line = f"{rec['id']} ({rec['record_type']}) :: {rec.get('summary', '').strip()}"
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search interface for the pattern history comprehensive index.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dimension", help="Search dimension from search_indices (e.g., pattern_type, severity, agents_involved).")
    group.add_argument("--attribute", help="Attribute key inside a record's attributes block (e.g., fragment_range, tca_classification).")
    group.add_argument("--record-id", help="Return a single record by id.")
    parser.add_argument("--key", help="Key to search within the dimension (e.g., continuation_pause).")
    parser.add_argument("--value", help="Value to match for an attribute search.")
    parser.add_argument("--index-path", type=Path, default=INDEX_PATH, help="Path to comprehensive_index.json")
    args = parser.parse_args()

    index = load_index(args.index_path)
    record_map = get_record_map(index)

    if args.record_id:
        record = record_map.get(args.record_id)
        if not record:
            print(f"No record found for id: {args.record_id}")
            return
        print(json.dumps(record, indent=2))
        return

    if args.dimension:
        if not args.key:
            raise SystemExit("Provide --key when using --dimension searches.")
        records = search_by_dimension(index, args.dimension, args.key)
        if not records:
            print(f"No matches for {args.key} in dimension {args.dimension}")
            return
        print(format_records(records))
        return

    if args.attribute:
        if args.value is None:
            raise SystemExit("Provide --value when using --attribute searches.")
        records = search_by_attribute(index, args.attribute, args.value)
        if not records:
            print(f"No matches where attribute {args.attribute} == {args.value}")
            return
        print(format_records(records))
        return


if __name__ == "__main__":
    main()
