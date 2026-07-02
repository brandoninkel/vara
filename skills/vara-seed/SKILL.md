---
name: vara-seed
description: >-
  One-command setup for the vara knowledge system — seeds the YouTube transcript corpus,
  runs the Haiku distill fleet, and builds + installs the /everything skill tree, taking a
  fresh clone of the vara repo to the fully-armed state. Use when the user says "vara-seed",
  "seed vara", "set up vara", "build the knowledge tree", or right after installing the vara
  pack when they want the self-refreshing pipeline live on their machine. The skill IS the
  opt-in to use the Workflow tool for the distill fleet.
---

# /vara-seed — from fresh clone to full orchestra

You are running the vara seeding pipeline. `$ARGUMENTS` may name a repo path; otherwise find
the cloned vara repo (look for `pipeline/ingest.py` + `claims/` under the cwd or ask). Work
from the REPO ROOT. Report progress after each phase. Everything is resume-safe — rerunning
this skill continues where it left off, never re-downloads or re-distills finished work.

## Phase 0 — Preflight (2 min)
1. Check tools: `yt-dlp --version` (if missing: `brew install yt-dlp` / `pipx install yt-dlp`),
   `python3 --version`. Both required. No API keys needed — ingestion is free.
2. Cookies (required at scale — YouTube bot-gates anonymous bulk pulls): ask the user which
   browser is logged into YouTube. On macOS prefer **Safari** (`--cookies-from-browser safari`);
   Chrome often fails while open (app-bound encryption). Firefox works on all platforms.
3. Ask the user: **quick seed** (~200 videos, ~15 min, good first taste) or **full seed**
   (~1,900 videos, 30–60 min ingest + a large distill run)? Optionally edit
   `pipeline/seeds.json` first — channels + queries define the corpus.

## Phase 1 — Ingest transcripts (free, their machine, their login)
```sh
# full seed (drop --max-per-channel to 20 and --max-per-query to 10 for the quick seed):
python3 pipeline/ingest.py --max-per-channel 150 --max-per-query 40 \
  --concurrency 4 --cookies-from-browser <their-browser>
```
Run in background; report progress every couple of minutes (`corpus/` file count). Expect
~99% capture. Failure modes + fixes: "Sign in to confirm you're not a bot" → cookies flag
missing/wrong browser; HTTP 429 → lower `--concurrency` to 2, rerun (resume-safe); "live event
will begin" → future stream, skip forever. NEVER work around ingestion limits by scraping
third-party transcript sites.

## Phase 2 — Batch
```sh
python3 pipeline/build_batches.py --word-budget 30000
```
Prints N batches → `pipeline/batches.json`. Remember N.

## Phase 3 — Distill (Haiku fleet via the Workflow tool — costs THEIR tokens)
Tell the user the honest cost before launching: roughly N batches ≈ N agents; the full ~1,900
video corpus ran ~28M subagent tokens on Haiku. Get an explicit go.
Then `mkdir -p claims` and invoke the **Workflow tool** with `scriptPath` =
`<repo>/pipeline/distill_workflow.js` and `args` =
```json
{ "corpusDir": "<abs repo>/corpus", "claimsDir": "<abs repo>/claims",
  "batchesPath": "<abs repo>/pipeline/batches.json", "batchCount": <N>,
  "domains": <the "domains" array from pipeline/domains.json> }
```
Progress = `claims/*.json` count climbing toward the corpus video count. If the session hits
a rate/usage limit mid-fleet: wait for reset, run `python3 pipeline/remaining_batches.py`,
re-invoke the Workflow with `batchesPath` = `pipeline/batches_remaining.json` and the new
count — completed videos are never re-distilled. (Skipping Phase 1–3 entirely is also valid:
the repo ships `claims/` pre-distilled — jump to Phase 4 to build from those.)

## Phase 4 — Build + install the tree (guarded)
```sh
python3 ~/.claude/skills/vara/tools/guard.py --snapshot   # note the SNAP dir it prints
python3 pipeline/build_skilltree.py --claims-dir claims --install
python3 pipeline/validate_skills.py ~/.claude/skills
python3 ~/.claude/skills/vara/tools/guard.py --verify --against <SNAP>
```
Expect: 17 skills installed, validation 0 errors, guard prints KEEP. If guard prints ROLLBACK,
the previous tree was restored — report the printed regressions instead of forcing it.

## Phase 5 — Report + cadence
Report: videos ingested, claims distilled, points/branches installed, ★ multi-source count,
and that a NEW session is needed to load the skills. Then offer (do not auto-create): a
weekly refresh schedule — rerun Phase 1 (only new uploads download), distill only new videos
(Phase 3 with `remaining_batches.py`), rebuild under guard. Wire it with the user's scheduler
of choice only on an explicit yes.
