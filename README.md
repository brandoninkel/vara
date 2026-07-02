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
