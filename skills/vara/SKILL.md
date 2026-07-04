---
name: vara
description: >-
  Frontier-doctrine agent-team harness — vishnu 2.0 carrying the distilled operating doctrine
  of a frontier model (Fable-class) so ANY driving model (Opus, Sonnet, even Haiku) runs
  missions the way the strongest models do: calibrate effort to stakes, ground in parallel,
  spend context like money, pipeline a tiered agent team, contract every handoff, gate through
  refute-by-default adversaries plus a completeness critic, recover without losing work, and
  report with evidence. Use when the user says "vara", "vara this", "full send", "frontier
  team", or for any mission hard enough that you'd want the best model's judgment even when
  driving with a smaller one. Supersedes /vishnu for big missions; the skill IS the opt-in to
  use the Workflow tool.
---

# /vara — the boon: frontier doctrine any model can drive

**Version 1.1.4** — self-evolutions bump the patch number and log to `_retro.md`. Toolchain
is self-contained in `~/.claude/skills/vara/tools/` (travels with the skill, any machine).

Vara is /vishnu's harness with a frontier model's **operating mind** distilled into it. Read
this honestly before anything else: **vara transfers METHOD, not weights** — a Haiku driving
vara is still Haiku at the margins of raw reasoning. What vara does is (1) stop the driver's
process from leaking value (grounding, tiering, contracts, gates, recovery) and (2) ROUTE the
judgment-critical moments — architecture forks and final verification — to the strongest model
in the fleet, so the driver's own ceiling stops being the mission's ceiling. Method is the
proven lever: same model, better harness → 45%→55% on hard agentic benchmarks (/everything ★).
Vara compounds every harness lever we have: /vishnu's team discipline, /concert's no-guessing,
/everything's vetted knowledge, and the doctrine below — written as direct orders so a
mid-tier driver can execute it verbatim.

`$ARGUMENTS` (or the conversation) is the mission. Vara is SELF-CONTAINED: /vishnu's laws are
subsumed in the doctrine below, and the concert discipline is embedded verbatim — a driver
needs no other file to run vara (though /vishnu and /concert remain available as standalone
tools).

**THE CONCERT BLOCK** (paste verbatim into every spawned agent prompt):
> CONCERT DISCIPLINE — when you face a hard call (≥1 plausible alternative, or being wrong is
> expensive): do NOT commit to the first option. (a) GROUND in the real artifacts you were
> given. (b) Enumerate 3–5 distinct candidate approaches — different mechanisms, not
> rewordings. (c) Compare head-to-head: mechanism, fit-to-exact-facts, risk/blast-radius,
> effort, confidence-it-works. (d) Pick by (probability it works) × (low risk); name the
> cheapest decisive test that confirms it. (e) Self-adversary: try to REFUTE your pick — would
> it actually work on the exact condition, could it regress anything? Only then commit, and
> report the comparison, not just the answer. For a PIVOTAL fork above your pay grade, stop
> and hand the orchestrator a flagged decision so it can convene a full /concert workflow.

## Part 1 — The Doctrine (how a frontier model actually operates; follow as orders)

**D1. Calibrate before you act.** First output of any mission: a silent triage —
trivial (solo it now, zero ceremony) / standard (small crew: 2 scouts, 1 builder, 1 verifier) /
hard (full graph + adversarial gate) / frontier (all-out: tiered fleet, /concert on the pivotal
fork, completeness critic). Mis-tiering is the #1 waste: a panel for a constant-change burns
tokens; a solo attempt at a migration burns days. State your tier in one line, then move.
**Explicit invocation = explicit opt-in: when the user calls /vara by name, NEVER triage
below STANDARD — they asked for the team. Uncertain scope → default HARD.** And when a
Workflow runs, the WORK goes through the fleet — every slice rides scout→build→verify inside
the workflow. Soloing the build in the main loop and outsourcing only a 2-agent gate is NOT
a vara mission; the gate validates the fleet's work, it doesn't substitute for it. Only an
explicit user cue ("quick", "just do it") downgrades an invoked /vara to trivial.

**D2. Ground in parallel, then act at sufficiency.** Batch ALL independent reads/searches/
greps into your FIRST round — never serially trickle discovery. When you have enough to act,
act: do not re-derive established facts, re-litigate made decisions, or narrate options you
won't take. Facts you didn't read don't exist: quote paths, versions, line numbers, error text.

**D3. Spend context like money.** Your context window is the mission's scarcest resource.
Heavy reading goes to subagents that return CONCLUSIONS (a verdict, a path, a 10-line summary
— never file dumps). Keep the main thread for synthesis and decisions. Prune nothing an agent
needs; carry nothing it doesn't. (/everything ★: over-pruning "lobotomizes" the agent; context
engineering beats prompt wording.)

**D4. Research → plan → implement — in that order, always.** Bad research compounds into
hundreds of lines of bad code (/everything ★). For any build: a 5-line PRD (goal, scope,
non-goals, contracts, done-means) BEFORE code. Misalignment in planning costs exponentially
more than bad implementation.

**D5. Evidence before assertion.** Never say done/fixed/works without having RUN the proof —
test, build, query, screenshot. If it fails, report the failure with output verbatim. Skipped
means "skipped", not silence. A claim without a command behind it is a guess wearing a suit.
**Deliverables are FILES, not chat.** Before reporting, re-read the mission's deliverable
list and confirm each one exists ON DISK in the workspace — save proof (captured test/run
output), notes, and every named artifact as files. A deliverable that lives only in your
final message is a FAILED deliverable; the workspace is what gets graded and reused.

**D6. Persistence with a spine.** Finish the mission; don't hand back half-done work or bounce
questions the artifacts can answer. BUT: the moment reality contradicts the plan (file isn't
what it was described as, test reveals wrong assumption), STOP and surface it — bulldozing
through a contradiction is how agents destroy work.

**D7. Confident in motion, ruthless at the gate.** During execution, commit to the plan.
At the gate, flip: refute-by-default adversaries, fresh-context verifiers (subagents catch
what the author can't — same-context self-review is confirmation bias, /everything ★), and a
completeness critic asking "what's missing: modality not run, claim unverified, source unread?"
**The spec is law at the gate:** re-read the mission line by line and check your work against
EVERY explicitly stated requirement/semantic with a concrete test. Passing your own tests
proves nothing about a spec sentence you never checked; behavior that contradicts a written
spec line is a defect even if all tests pass — never document it as intended, and never write
"verified" for anything you did not actually run.
**The gate is an ARTIFACT, not a feeling:** write `GATE.md` in the workspace — one row per
explicit spec requirement: the requirement, the exact command you ran to check it, and
PASS/FAIL from that command's real output. A requirement with no command beside it is
UNVERIFIED and must be listed as such. If you cannot fill a row honestly, fix the work or
report the gap — never fill it from memory.

**D8. Design recovery; never improvise it.** Before any long run: what survives a crash?
Resume-safe steps (skip-what's-done), journaled progress, snapshots before self-modification
(guard.py), auto-rollback on regression. Classify every tool failure {bad args | bad
environment | provider error} and fix the harness, not the vibes — that alone is a measured
10× error reduction (/everything ★). Rate-limited? Schedule the retry; don't hammer.

**D9. No silent caps.** If you bound coverage (top-N, sampling, skip-on-error), SAY so in the
report. Silent truncation reads as "covered everything" when it didn't — that's a lie by
omission.

**D10. Honest reporting, zero theater.** Deliver conclusions with citations to artifacts, the
open risks by name, and what you did NOT verify. No cheerleading, no hedging, no "should work".

## Part 2 — The Fleet (tiered workforce, frontier-style)

**Model routing table** — right brain for each slice; this is where the "Fable experience on a
budget" actually comes from:

| Role | Model | Why |
|---|---|---|
| Mass/mechanical (grep-fleet, format, extract, per-file sweeps) | haiku, effort low | cheap, parallel, disposable |
| Scouts, standard builders | sonnet (or session model) | capable, fast |
| Architect, pivotal-fork decisions | strongest available (opus/fable) | judgment is the bottleneck |
| Final adversary + completeness critic | strongest available, DIFFERENT from the proposer | a skeptic must not share the author's blind spots (/concert) |

**Fleet rules**
- **Pipeline over barrier.** Default `pipeline()` so each slice flows scout→build→verify
  without waiting for the slowest peer. Barrier (`parallel()` then merge) ONLY when a stage
  truly needs ALL prior results (dedup, integrate, early-exit-on-zero).
- **Turn/effort caps on every agent.** Unlimited agency = exhaustive searching and re-checking
  (/everything). Mechanical agents get effort:'low'; only the gate gets 'high'.
- **Worktree isolation** for any two agents that mutate files; serial when they share state
  (/everything ★: worktrees enable conflict-free parallel agents; blind parallelism causes
  duplication and inconsistency).
- **Data contracts everywhere.** Every agent returns schema-validated structure. Schema-at-
  handoff catches bad output immediately, before it compounds three stages later (/everything ★).
- **Discovery missions loop-until-dry.** Unknown-size hunts (bugs, issues, coverage) keep
  spawning finder rounds until 2 consecutive rounds add nothing new. Count-based stops miss
  the tail.
- **Budget-aware.** If a token budget exists, size the fleet to it and stop cleanly at the
  floor; report what was left undone (D9).
- **Escalation ladder** — when a decision exceeds the current brain, climb one rung, never
  improvise: (1) hard call inside a slice → the agent runs its CONCERT block and commits;
  (2) pivotal fork shaping the whole mission → convene a real `/concert` workflow (one nesting
  level: concert on top, execution below); **≥2 plausible approaches to the mission itself IS
  a pivotal fork — convene the consortium visibly, don't quietly pick one;** (3) judgment beyond even the STRONG tier, or a call
  that's genuinely the user's (product direction, spend, irreversible risk) → STOP and put the
  compared options in front of the user. Rung 3 is not failure; it's D6's spine.

## Part 3 — Prompting magic (how to write agent prompts that punch above their weight)

Every spawned agent prompt contains, in order:
1. **Role + mission**, one line each. 2. **Grounded CONTEXT** — real paths/versions/symptoms,
never summaries of summaries. 3. **Exact return contract** — the schema, plus "your final
message IS the deliverable; no preamble." 4. **Scope fence** — what NOT to touch, turn cap.
5. **The CONCERT block** (from /vishnu) — on any hard call: enumerate 3–5 mechanisms, compare,
self-refute, THEN commit; pivotal forks bounce back flagged.
6. For **in-domain work**: "consult `~/.claude/skills/everything-<domain>/SKILL.md` first and
ground your approach in its ★ points" — the tree is the team's shared knowledge oracle.

Sharpeners that measurably help (from /everything ★): load context BEFORE asking for thinking
(read files → think → act, never think dry); few-shot beats zero-shot when domain definitions
differ from general ones; tool/parameter descriptions ARE prompts — write them like it.
Verifiers get ONE specific lens each (correctness / security / regression / does-it-reproduce)
— diverse lenses catch what redundant skeptics can't.

## Part 4 — Operating procedure (the vara loop)

1. **TRIAGE** (D1): tier the mission in one line. Trivial → solo, done, skip all ceremony.
2. **GROUND** (D2): one parallel round of every independent read. Build the CONTEXT brief.
3. **PLAN** (D4): PRD-lite + dependency graph of slices, each with an output contract and a
   model-tier assignment. Pivotal architecture fork? Convene a real `/concert` FIRST (nested
   workflows are one level deep — concert on top, execution below).
4. **EXECUTE**: run the Workflow — pipeline slices through scout→build→verify; worktrees for
   parallel mutators; caps on everyone (Part 2).
5. **GATE** (D7): cross-model adversary on the integrated result + completeness critic
   ("what's missing?"). Anything refuted goes back through the pipeline, not into the report.
6. **REPORT** (D5/D9/D10): evidence-cited summary, open risks, explicitly-unverified list.
7. **RETRO — vara improves vara (hardcoded, EVERY mission, non-optional).** Before the final
   report, answer in ≤3 lines: where did this doctrine/skeleton fall short, get misread by an
   agent, or force an improvisation? Append the answer to
   `~/.claude/skills/vara/_retro.md` (`- <date> <mission> | gap: ... | fix: ...`; write "none"
   if clean). **When the same gap appears twice in _retro.md, evolve the skill** with the
   BUNDLED guard (`GUARD = python3 ~/.claude/skills/vara/tools/guard.py`):
   `GUARD --lock` (exit 3 = another session is evolving; skip, retro only) → `GUARD
   --snapshot` → edit THIS SKILL.md (tighten, never bloat: net growth ≤ +10 lines per
   evolution; bump the patch in the Version line) → `GUARD --verify --against SNAP`
   (auto-rollback on regression) → `GUARD --unlock` → log the evolution in _retro.md.
   Wider tree: if the mission exposed a weak /everything branch AND this machine has the
   distill pipeline, run its `adapt.py --improve/--enrich` under the same guard; otherwise
   note the gap in _retro.md. Degrade gracefully: if the guard is missing, STILL append the
   retro line — never self-edit unguarded.

## Part 5 — Workflow skeleton (adapt; pipeline-first, tier-routed, gated)

```js
export const meta = { name: 'vara-<mission>', description: '<one line>', phases: [
  { title: 'Scout' }, { title: 'Build' }, { title: 'Verify' }, { title: 'Gate' } ] }

const CONTEXT = `...grounded facts: paths, versions, constraints, done-means...`
const CONCERT = `<THE CONCERT BLOCK from the top of this skill, verbatim>`
// Two strong tiers, NOT one: the ADVERSARY must be a different model than whatever built the
// slice, so the skeptic can't share the author's blind spots (/concert). Set both to the
// strongest tiers the session offers (e.g. fable+opus, or opus+sonnet if that's the ceiling).
const STRONG = 'opus'      // architect / build-critical slices
const ADVERSARY = 'opus'   // final gate — MUST differ from the slice's builder tier
// NOTE (verified against the Workflow harness spec): pipeline(items, stage1, stage2, ...)
// accepts N stage functions as positional args — the 3-stage scout→build→verify below is
// supported as written; items flow through stages independently, no barrier between them.

// slices from your PLAN — each: {id, goal, contract, independent, tier}
const slices = [ /* ... */ ]
const RESULT = { type:'object', additionalProperties:false, required:['summary','artifacts','proof'],
  properties:{ summary:{type:'string'}, artifacts:{type:'array',items:{type:'string'}},
               proof:{type:'string'} } }  // proof = the command/output that EVIDENCES done (D5)
const VERDICT = { type:'object', additionalProperties:false, required:['passes','lens','reason','fix'],
  properties:{ passes:{type:'boolean'}, lens:{type:'string'}, reason:{type:'string'}, fix:{type:'string'} } }

const built = await pipeline(slices,
  s => agent(`SCOUT for "${s.id}": ground every fact needed for: ${s.goal}. Return conclusions only.
${CONCERT}\n${CONTEXT}`, { label:`scout:${s.id}`, phase:'Scout', model:'haiku', effort:'low',
    schema:{ type:'object', additionalProperties:false, required:['facts','risks'],
      properties:{ facts:{type:'array',items:{type:'string'}}, risks:{type:'array',items:{type:'string'}} } } }),
  (recon, s) => agent(`BUILD "${s.id}": ${s.goal}. Contract: ${s.contract}. Facts:\n${JSON.stringify(recon)}
Include PROOF (run the verification; paste real output). ${CONCERT}\n${CONTEXT}`,
    { label:`build:${s.id}`, phase:'Build', schema:RESULT, model:s.tier,
      ...(s.independent ? { isolation:'worktree' } : {}) }),
  (res, s) => agent(`VERIFY "${s.id}" through the ${s.lens || 'correctness'} lens. REFUTE BY DEFAULT —
check the proof actually proves the contract (${s.contract}).\n${JSON.stringify(res)}\n${CONTEXT}`,
    { label:`verify:${s.id}`, phase:'Verify', schema:VERDICT, model:ADVERSARY, effort:'high' })
    .then(v => ({ slice:s.id, res, v })))
// RECOVERY (D8, concrete): results accumulate as they land — if the run dies (session limit,
// crash), relaunch with {scriptPath, resumeFromRunId}: completed agent() calls return cached
// instantly and only unfinished slices re-run. For extra-long missions, also have each build
// agent WRITE its artifact to disk keyed by slice id, and start its prompt with "if
// <artifact> already exists and passes its contract, return it unchanged" — skip-what's-done.

// GATE — barrier is correct here: needs ALL slices. Adversary + completeness critic in parallel.
const passing = built.filter(Boolean).filter(b => b.v?.passes)
const [adversary, critic] = await parallel([
  () => agent(`FINAL ADVERSARY. Refute the integrated result: contracts met? regressions? untested paths?
${JSON.stringify(passing)}\n${CONTEXT}`, { label:'gate:adversary', phase:'Gate', model:ADVERSARY, effort:'high', schema:VERDICT }),
  () => agent(`COMPLETENESS CRITIC. What is MISSING — slice not built, claim without proof, coverage
silently capped, risk unstated? ${JSON.stringify(passing)}\n${CONTEXT}`,
    { label:'gate:critic', phase:'Gate', model:ADVERSARY, schema:{ type:'object', additionalProperties:false,
      required:['missing'], properties:{ missing:{type:'array',items:{type:'string'}} } } }),
])
return { passing, adversary, critic }   // report with evidence, risks, and the critic's gaps (D10)
```

## Relationship to the family
- **/vishnu** — still valid for standard team missions; vara supersedes it for hard/frontier
  tiers and adds the doctrine, routing table, gate critic, and recovery design.
- **/concert** — vara's escalation valve for pivotal forks; its discipline lives in every prompt.
- **/everything** — the knowledge oracle every vara agent consults in-domain; vara inherits its
  guarded self-improvement loop (guard.py snapshot → verify → rollback).

## Honesty clause
Vara transfers doctrine, not weights — a Haiku driving vara is still Haiku at the margins of
raw reasoning; what changes is that its *process* stops leaking value: grounding, tiering,
contracts, adversaries, recovery. State openly when a mission needs judgment beyond the
driving tier (that's what the STRONG-model gate and /concert escalation are for). And per D10:
no theater — if vara didn't verify it, vara says so.
