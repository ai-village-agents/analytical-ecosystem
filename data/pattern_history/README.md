# pattern_history database

This directory holds append-only records of pattern shifts, related baseline segments, and coordination notes.

## Layout
- `records/` — individual pattern shift records.
- `velocity_baselines/` — baseline velocity segments and their context.
- `multi_agent_logs/` — coordination and agent-to-agent interaction logs.
- `predictive_catalog/` — predictive fragments and forecasts.
- `tca_database/` — title-content asynchrony (TCA) observations.
- `indices/` — search indices, cross-references, and the append-only ledger.

## Schema
- `pattern_history_schema.json` defines a shared schema across record types with required fields for `id`, `record_type`, `timestamp`, `provenance`, and `content`.
- `record_type` determines the target subdirectory:
  - `shift_record` → `records/`
  - `velocity_baseline` → `velocity_baselines/`
  - `multi_agent_log` → `multi_agent_logs/`
  - `predictive_fragment` → `predictive_catalog/`
  - `tca_record` → `tca_database/`

## Append-only validation
- `validation_script.py validate <file>` checks schema compliance, timestamp formatting (timezone required), provenance completeness, and path-category alignment.
- `validation_script.py register <file>` performs validation and appends an entry to `indices/append_only_ledger.jsonl` with the file hash. If a file already appears in the ledger with a different hash, the command fails, preventing mutation.
- Ledger entries are JSONL to keep the log append-only and diff-friendly. Avoid hand-editing existing lines; new entries should only be appended.

## Importing existing data
- Use `import_existing_data.py --record-type <type> [--source <dir>] --execute` to copy legacy JSON files (default source: `data/pattern_observations`) into the appropriate subdirectory and register them.
- Omit `--execute` to perform a dry run and see where files would land.

## Contributing new records
1. Write the JSON record that satisfies `pattern_history_schema.json`.
2. Place it in the correct subdirectory for its `record_type`.
3. Run `validation_script.py register <path>` to validate and append to the ledger.
4. Commit the new file and the updated ledger together to preserve immutability guarantees.
