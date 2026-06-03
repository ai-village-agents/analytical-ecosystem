#!/usr/bin/env python3
"""
Utility for importing existing pattern observations into the pattern_history layout.

Current behavior:
- Scans a source directory for JSON records.
- Copies them into the correct destination subdirectory based on --record-type.
- Validates and registers them using validation_script.py when run with --execute.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import List, Optional

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
DEFAULT_SOURCE = PROJECT_ROOT / "data" / "pattern_observations"

# Local import without relying on package installation.
sys.path.insert(0, str(CURRENT_DIR))
from validation_script import RECORD_DIRECTORIES, validate_file  # type: ignore


def gather_sources(source_dir: Path) -> List[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    return sorted([p for p in source_dir.glob("*.json") if p.is_file()])


def destination_dir(record_type: str) -> Path:
    subdir = RECORD_DIRECTORIES[record_type]
    target = CURRENT_DIR / subdir
    target.mkdir(parents=True, exist_ok=True)
    return target


def stage_record(path: Path, record_type: str, execute: bool) -> Path:
    target_dir = destination_dir(record_type)
    target = target_dir / path.name
    if execute:
        shutil.copy2(path, target)
        validate_file(target, expected_type=record_type, register=True)
    return target


def import_records(record_type: str, source_dir: Path, execute: bool) -> List[Path]:
    results: List[Path] = []
    for src in gather_sources(source_dir):
        results.append(stage_record(src, record_type, execute))
    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Import legacy pattern observations into pattern_history.")
    parser.add_argument("--record-type", choices=RECORD_DIRECTORIES.keys(), required=True, help="Destination record type.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Directory containing source JSON files.")
    parser.add_argument("--execute", action="store_true", help="Copy files and register them; otherwise perform a dry run.")
    args = parser.parse_args(argv)

    copied = import_records(args.record_type, args.source, args.execute)
    action = "staged" if args.execute else "previewed"
    for path in copied:
        print(f"{action}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
