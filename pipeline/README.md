# /everything — self-learning AI skill tree pipeline

Builds a global Claude skill tree distilled from thousands of top AI YouTube
videos, vetted against the videos' comments as a bullshit meter. All ingestion
is **free** — `yt-dlp` does discovery + transcripts + comments with no API key
and no quota. Whisper is only a fallback for the rare caption-less video.

## Flow

```
seeds.json ─┐
            ▼
  ingest.py  ──►  corpus/<id>.json   (transcript + comments + metadata)
            │
            ▼
build_batches.py ──►  batches.json    (size-bounded; respects 1000-agent cap)
            │
            ▼
distill_workflow.js ─►  claims/<id>.json   (Haiku fleet; scored, comment-vetted)
   (run via the Workflow tool)
            │
            ▼
build_skilltree.py ──►  skilltree_build/   (cull → cluster → group by domain)
            │  --install
            ▼
   ~/.claude/skills/everything + everything-<domain>   (global)
```

## Cookies (required at scale)

YouTube throws "Sign in to confirm you're not a bot" once you make many requests
from one IP. Fix: authenticate yt-dlp as your own logged-in session with
`--cookies-from-browser safari` (works cleanly on macOS; reads Safari's cookie
file — Terminal needs Full Disk Access). Chrome is unreliable here (app-bound
encryption hangs while Chrome is open). This is NOT evasion — it's logging in as
you, and it keeps transcripts + comments + metadata in one tool. Pass it to
every ingest command. Keep concurrency moderate (~4) even with cookies.

## Commands

```bash
# 1. INGEST (free, no key — but pass cookies at scale). Proof:
python3 pipeline/ingest.py --only "Karpathy" --max-per-channel 5 --with-comments --cookies-from-browser safari
# Full sweep:
python3 pipeline/ingest.py --max-per-channel 150 --max-per-query 40 --concurrency 4 --cookies-from-browser safari
# Comments pass (bullshit-meter signal) over what's already ingested:
python3 pipeline/ingest.py --augment-comments --concurrency 3 --cookies-from-browser safari
# Resume-safe + self-healing: rerun anytime; done videos skip, bot/429 failures retry.

# 2. BATCH
python3 pipeline/build_batches.py --word-budget 32000

# 3. DISTILL  (Haiku fleet via the Workflow tool, scriptPath=pipeline/distill_workflow.js)
#    args = { corpusDir, claimsDir, batches:[...from batches.json], domains:[...from domains.json] }

# 4. BUILD + INSTALL
python3 pipeline/build_skilltree.py            # stage for review
python3 pipeline/build_skilltree.py --install  # deploy to ~/.claude/skills
```

## Files
- `seeds.json`   — channels (the intelligent AI circle) + search queries. Editable; grows.
- `domains.json` — controlled vocab = first-level branches of the tree.
- `ingest.py`    — yt-dlp ingester: srv1 transcripts, top comments, metadata. Resume + retry.
- `build_batches.py` — packs corpus into agent-sized batches.
- `distill_workflow.js` — one Haiku agent per batch → scored claims files.
- `build_skilltree.py` — cull (bullshit meter) → cross-source cluster → emit skill tree.

## Self-learning
Rerun the flow on fresh uploads; resume-safe ingest only pulls new videos, the
fleet re-distills, and the tree regenerates with re-vetted knowledge.
