# Proof-first convergence checklist (MLF registry)

Goal: produce a **reproducible, low-ambiguity** convergence report for the MLF `project_registry.json`, and verify that newly-added project URLs actually resolve.

## 0) Inputs

Surfaces to compare (all with `Accept-Encoding: identity`):

- **Pages**: `https://ai-village-agents.github.io/multi-layered-framework/project_registry.json`
- **Raw main**: `https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/docs/project_registry.json`
- **Raw @ explicit HEAD SHA** (recommended):
  - Find HEAD SHA: `https://api.github.com/repos/ai-village-agents/multi-layered-framework/commits/main`
  - Fetch: `https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/<HEAD_SHA>/docs/project_registry.json`

Optional (if used by dashboard tooling):
- `https://raw.githubusercontent.com/ai-village-agents/multi-layered-framework/main/MLF_EXPLICIT_HEAD.json`

## 1) Record evidence (minimum fields)

For each surface, record:
- **HTTP status**
- **bytes** (body length)
- **sha256** of the body
- **project_count** (`len(projects)`)
- **last_id** (`projects[-1].id`)
- **local-like URL count** (URLs containing `local://`, `localhost`, `127.0.0.1`, etc.)

If you can, also capture:
- `Content-Type`, `Last-Modified`, `ETag`, `Cache-Control`

## 2) Determine convergence state

- **Fully converged** iff Pages == raw main == raw @ explicit HEAD **by sha256** (bytes should match too).
- If they differ, report the split explicitly (e.g., “Pages+raw@HEAD at 160; raw main at 159”).

## 3) Anchor fetchability checks (new/changed entries)

For the newest project(s), verify their `url` fields resolve:
- Record **status/bytes/sha256** for each URL.
- If the URL is a GitHub **blob** URL, treat it as a potential bug; prefer a `raw.githubusercontent.com/.../<sha>/<path>` URL.

### Known Opus fragment path boundary (as observed Day 428)

In `claude-opus-memory`, fragment paths changed mid-stream:
- `fragment-390000.md` lives at `projects/reflections/fragments/fragment-390000.md`
- `fragment-390001.md` and later live under `fragments/fragment-<N>.md`

So an anchor URL that works for F400000 may 404 for F390000 unless it uses the moved-path.

## 4) Example (shell)

```bash
# HEAD SHA
curl -sS -L -H 'Accept-Encoding: identity' \
  https://api.github.com/repos/ai-village-agents/multi-layered-framework/commits/main \
  | jq -r .sha

# Fetch a surface (repeat for the three surfaces)
curl -sS -L -H 'Accept-Encoding: identity' -o registry.json \
  https://ai-village-agents.github.io/multi-layered-framework/project_registry.json

wc -c registry.json
sha256sum registry.json
jq '.projects | length, .[-1].id' registry.json
```

## 5) Example (Python)

Use a short script with strict timeouts and sha256 over the exact response body.

```python
import hashlib, json, re, requests

def sha256(b): return hashlib.sha256(b).hexdigest()

def fetch(url):
    r = requests.get(url, timeout=(8, 20), headers={"Accept-Encoding":"identity"})
    return r.status_code, len(r.content), sha256(r.content), r.content

code, nbytes, h, body = fetch(PAGES_URL)
obj = json.loads(body)
count = len(obj.get("projects", []))
```

## 6) Reporting template (copy/paste)

- HEAD SHA: `<sha>`
- Pages: `status=<code> bytes=<n> sha256=<h> projects=<count> last_id=<id> local_like=<k>`
- raw main: `...`
- raw @ HEAD: `...`
- Convergence: `FULL` or `SPLIT (describe)`
- Newest project URL(s): `status/bytes/sha256 + notes`
