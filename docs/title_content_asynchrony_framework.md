# Title-Content Asynchrony Analysis Framework
Defines, detects, and documents discrepancies between commit/PR titles and the actual repository content to prevent misleading velocity metrics and coordination drift.

## 1) Definition and Classification System
- **Title-content asynchrony (TCA):** any gap between what a title/commit message asserts and what the diff delivers.
- **Classes:**
  - `anticipatory_title`: title promises work that is absent in the diff (e.g., mentions a feature that is not yet added).
  - `batch_processing_delay`: title references multiple items but only a subset landed because of batching/queue delays.
  - `numbering_convention_discrepancy`: numbering or fragment IDs in the title do not match filenames/paths (e.g., F170000 vs F169999).
  - `content_staging`: partial implementation landed; title is accurate at intent level but scope-delivery is incomplete or staged behind flags.
- **Attributes per finding:** `scope` (files/paths touched), `claimed_scope` (title assertions), `delta_scope` (difference), `expected_follow-ups`, `risk_level` (low/med/high based on user-facing impact and velocity distortion potential).

## 2) Detection Methods
- **File listing verification vs title claims:** enumerate changed files (`rg --files -g'*'` or VCS diff listing) and map against title claims to confirm presence/absence of asserted paths, features, or IDs.
- **Semantic diff inspection:** check whether code paths that title references are actually modified (functions, flags, configs).
- **Numbering cross-check:** extract IDs/versions in titles and compare to filenames, schema versions, or fragment markers inside files.
- **Batch intent validation:** when titles mention multiple fixes/features, count resolved items vs claimed items; tag leftover items as pending batch fragments.
- **Content staging confirmation:** detect feature flags, TODO markers, or placeholder stubs; if present, mark as staging and require explicit follow-up title alignment.
- **Automated heuristics:** lint rules that flag mismatched IDs, unmodified asserted files, or absent symbols referenced in titles; require manual agent confirmation before closure.

## 3) Multi-Agent Coordination Protocols for Verification
- **Roles:** `title_intent_mapper` (extracts claims), `content_verifier` (maps diff to claims), `numbering_auditor` (ID/version parity), `historian` (archives evidence), `arbiter` (issues verdict and remediation).
- **Protocol:** T0 detection → T0+1 extract claims → T0+2 run file listing & numbering checks → T0+3 dual-agent confirmation (primary + secondary) → T0+4 publish TCA record with remediation → T0+5 link to velocity adjustment notes.
- **Conflict handling:** if agents disagree, arbiter requires targeted checks (e.g., specific file inspection) before closure; no velocity updates until consensus.
- **Remediation:** amend title, split batch into scoped commits, or land missing content; document chosen path in the TCA record.

## 4) Impact Assessment on Velocity Calculations
- **Prevent inflated throughput:** exclude or down-weight commits with `anticipatory_title` or `content_staging` until matching content lands.
- **Cycle-time accuracy:** tie lead-time calculations to actual delivery, not to anticipatory titles; adjust timelines when batch delays are logged.
- **Fragment/ID continuity:** reconcile numbering discrepancies before computing fragment-based velocity to avoid off-by-one artifacts.
- **Reporting:** annotate dashboards with TCA-adjusted velocity and flag where title misalignment could mask slowdowns or overstated scope completion.

## 5) Historical Documentation Standards
- **Storage:** append structured TCA records to `/data/title_content_asynchrony/` (JSON) and summarize in `/docs/title_content_asynchrony_framework.md` changelog notes.
- **Required fields per record:** `tca_id`, `timestamp`, `title_text`, `claimed_scope`, `observed_scope`, `classification`, `delta_scope`, `affected_fragments`, `agents_involved`, `verdict`, `remediation`, `velocity_adjustment`, `provenance` (hashes/log pointers).
- **Verification requirements:** at least two agents sign off (primary + secondary) with timestamps; preserve file listing evidence snapshots.
- **Linkage:** every TCA record ties to commits/PRs and to any impacted pattern-shift or velocity reports to maintain traceability.
