# Pattern History Comprehensive Index

Paths:
- Index: `data/pattern_history/indices/comprehensive_index.json`
- Search API: `data/pattern_history/indices/search_api.py`

## Structure
- `metadata`: database info, source ledger, summary statistics (total_records, records_by_type, timestamp_range).
- `records`: flattened metadata per ledger entry with id, type, timestamp, path, hash, links, and useful attributes (fragment_range, severity, agents, predictive signals).
- `cross_references`: relationships between records (e.g., F170000 continuation pause ↔ TCA ↔ velocity baseline ↔ predictive fragments).
- `day_427_summary`: Day 427 roll-up (total fragments, pattern shifts observed, multi-agent coordination events).
- `search_indices`: ready-made dimensions for quick lookups (fragment_range, pattern_type, severity, agents_involved, tca_classification, predictive_signal, etc.).

## Usage
Run searches from the repository root:
- Dimension lookup: `python data/pattern_history/indices/search_api.py --dimension pattern_type --key continuation_pause`
- Attribute match: `python data/pattern_history/indices/search_api.py --attribute severity --value major`
- Agent lookup: `python data/pattern_history/indices/search_api.py --dimension agents_involved --key GPT-5.2`
- Direct record: `python data/pattern_history/indices/search_api.py --record-id f170000_tca`

The CLI prints concise lines (`id (type) :: summary`). Use `--record-id` for full JSON.

## Notes
- Source ledger: `data/pattern_history/indices/append_only_ledger.jsonl`.
- Day 427 totals reference `docs/real_time_implementation_summary.md` (140,250+ fragments).
- Multi-agent coordination counts are drawn from `f170000_tca_detection_coordination` events.
