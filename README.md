# vara — frontier-doctrine agent-team harness for Claude Code

A skill family that makes any Claude model run hard missions the way frontier models do:
ground in real artifacts, tier a subagent team, contract every handoff, gate through
refute-by-default adversaries, recover without losing work — and **self-evolve under a
rollback guard**.

| Skill | What it does |
|---|---|
| **/vara** | The apex: tiered agent-team missions with doctrine D1–D10, model routing, completeness critic, escalation ladder, guarded self-evolution. Self-contained (bundled toolchain). |
| **/vishnu** | Lighter team harness (ground → decompose → build → adversarial gate). |
| **/concert** | Compare-before-commit consortium for hard decisions — parallel research, ranked matrix, adversarial verify. |
| **/everything** (optional) | 17-skill knowledge tree: ~14,000 vetted, source-cited points distilled from ~1,900 top AI talks (Karpathy, Anthropic, AI Engineer…), 16 domains. |

## Install

**As a plain skills pack (any machine):**
```sh
git clone <this-repo> && cd vara-plugin
./install.sh                     # core: vara + vishnu + concert
./install.sh --with-everything   # + the knowledge tree
```

**As a Claude Code plugin:** this repo carries `.claude-plugin/plugin.json`; add it via your
plugin marketplace flow (`/plugin` in Claude Code) or point Claude Code at the repo.

Open a **new** session (skills load at session start) and run `/vara <mission>`.

## Requirements
- Claude Code with the Workflow/subagent tooling (vara/vishnu/concert spawn agent teams).
- `python3` (stdlib only) for the self-evolution guard.
- Works driven by any model tier; strongest available tier is auto-reserved for
  architect + adversary roles per vara's routing table.

## The full orchestra: refresh the knowledge tree yourself
This repo ships the ENTIRE pipeline (`pipeline/`) plus the distilled claims dataset
(`claims/`, ~14.5k source-attributed knowledge points) — so the /everything tree is not
frozen for you:

```sh
# per-branch re-mine from the shipped claims (works out of the box):
python3 pipeline/adapt.py --improve agents
# full tree rebuild + install from claims:
python3 pipeline/build_skilltree.py --claims-dir claims --install
# GROW the corpus yourself (your machine, your YouTube login, your tokens):
python3 pipeline/ingest.py --max-per-channel 50 --concurrency 4 --cookies-from-browser safari
python3 pipeline/build_batches.py            # then run pipeline/distill_workflow.js via the
                                             # Workflow tool, then build_skilltree --install
```

**What is deliberately NOT included:** the raw transcript corpus (~55M). Republishing 1,900
creators' full transcripts would be a copyright problem — so you regenerate it locally with
your own YouTube session (that's what `ingest.py` does; it's free, no API key). Distilling
costs your own model tokens. Everything else — ingester, batcher, Haiku-fleet distill
workflow, tree builder, self-adapt tooling, guard, analyzers, seeds — is here.

## Self-evolution (and how it stays safe)
Every /vara mission ends with a 3-line retro appended to `~/.claude/skills/vara/_retro.md`.
When the same gap shows up twice, vara edits its own SKILL.md — but only through the bundled
guard: concurrency **lock** → **snapshot** → edit → **verify** (auto-**rollback** on any
regression) → unlock → version bump. Never edits unguarded; snapshots live in
`~/.claude/skills_backups/`.

## Honesty clause
vara transfers **method, not weights** — a small model driving vara is still a small model at
raw-reasoning margins. What changes: its process stops leaking value, and judgment-critical
moments route to the strongest model in your fleet. Per the corpus this pack distills, harness
craft moved the same model 45%→55% on hard agentic benchmarks. That's the lever this ships.
