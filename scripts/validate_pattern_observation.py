#!/usr/bin/env python3
"""
Validate pattern observation JSON files against the pattern_observation_schema.json.
Provides detailed error reporting to help align records with the framework.
"""

import argparse
import json
import sys
from pathlib import Path


def load_validator(schema_path: Path):
    try:
        from jsonschema import Draft7Validator
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency hint
        print(
            "The 'jsonschema' package is required. Install with:\n"
            "  pip install jsonschema",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    with schema_path.open("r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    # Validate the schema itself to catch typos early.
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def iter_json_targets(paths):
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            yield from sorted(path.rglob("*.json"))
        elif path.suffix.lower() == ".json":
            yield path
        else:
            print(f"Skipping non-JSON target: {path}", file=sys.stderr)


def format_error_path(error):
    if not error.path:
        return "<root>"
    segments = []
    for part in error.path:
        if isinstance(part, int):
            segments.append(f"[{part}]")
        else:
            if segments:
                segments.append(f".{part}")
            else:
                segments.append(str(part))
    return "".join(segments)


def validate_file(validator, path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        return False, [f"Invalid JSON ({path}): line {exc.lineno} column {exc.colno} - {exc.msg}"]

    errors = sorted(validator.iter_errors(payload), key=lambda e: (list(e.path), e.message))
    if not errors:
        return True, []

    formatted = []
    for err in errors:
        location = format_error_path(err)
        formatted.append(f"{location}: {err.message}")
    return False, formatted


def main():
    repo_root = Path(__file__).resolve().parent.parent
    default_schema = repo_root / "standards" / "schemas" / "pattern_observation_schema.json"
    default_data_dir = repo_root / "data" / "pattern_observations"

    parser = argparse.ArgumentParser(
        description="Validate pattern observation JSON documents against the standard schema."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=[default_data_dir],
        help="Files or directories to validate (defaults to data/pattern_observations).",
    )
    parser.add_argument(
        "--schema",
        default=default_schema,
        help=f"Path to schema file (defaults to {default_schema}).",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        return 1

    validator = load_validator(schema_path)
    any_failures = False

    targets = list(iter_json_targets(args.targets))
    if not targets:
        print("No JSON targets found.", file=sys.stderr)
        return 1

    for path in targets:
        ok, errors = validate_file(validator, path)
        if ok:
            print(f"[OK] {path}")
        else:
            any_failures = True
            print(f"[FAIL] {path}")
            for msg in errors:
                print(f"  - {msg}")

    return 1 if any_failures else 0


if __name__ == "__main__":
    sys.exit(main())
