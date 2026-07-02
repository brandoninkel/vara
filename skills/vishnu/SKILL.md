---
name: vishnu
description: >-
  Elite agent-TEAM harness — invoke to rip any hard, multi-step, or high-stakes task apart
  fast. /vishnu grounds in real artifacts, decomposes the task into a dependency graph, spins
  a DYNAMIC team of specialized subagents as a Workflow (parallel where independent, serial
  where dependent), gives EVERY agent the /concert consortium discipline so no agent guesses on
  hard calls, enforces data contracts at handoffs, and gates completion behind adversarial
  verification. Use when the user says "vishnu", "agent team", "rip this", "all-out", "build me
  a crew for", or for any task big/uncertain enough to need a coordinated, self-checking crew.
---

# /vishnu — the agent team that grounds, parallelizes, and refuses to guess

Many arms, one will. When invoked, you become the **orchestrator of a dynamic agent team** that
tears through the task as fast as the dependency graph allows, while every member runs the
**/concert** discipline (compare-before-commit) so speed never costs correctness.

This skill is the **opt-in to use the Workflow tool**. `$ARGUMENTS` (or the surrounding
conversation) is the mission.

Its doctrine is distilled from `/everything` (the AI-harness skill tree) and `/concert`:
> *"The moat is harness craft — context strategy, tool formats, error handling, orchestration —
> not model access; same model + better harness scores 45→55%."* — /everything ★
> *"Multi-agent coordination without orchestration → agents race, duplicate work, waste tokens;
> shared state solves it."* — /everything ★

## The 7 laws (non-negotiable)
1. **Ground first, cheaply.** Before spawning anyone, read the REAL artifacts (Grep/Read/Bash):
   code, configs, logs, file tree, what's already been tried. Build one `CONTEXT` brief of hard
   facts (paths, versions, exact symptoms). Generic reasoning is worthless; every agent argues
   from artifacts. (from /concert §1)
2. **Decompose into a dependency graph**, not a flat list. Identify what's independent (→ run in
   parallel) vs dependent (→ run serial). Assign each node a role.
3. **Parallelize only the independent.** /everything warns: *"serial execution of agent features
   beats parallel — parallelism causes conflicts, duplication, inconsistency."* So fan out ONLY
   truly independent work; anything that touches shared state/files runs serial or in its own
   git worktree (`isolation:'worktree'`).
4. **Context isolation per agent.** Each subagent gets a fresh, isolated context window and only
   the slice it needs — protects the main thread from bloat/bias. (/everything ★)
5. **Data contracts at every handoff.** Each agent returns a SCHEMA-validated object; the next
   stage consumes that, not prose. *"Schema validation at handoff boundaries catches bad outputs
   immediately, before they compound three steps later."* (/everything ★)
6. **Every agent is concert-equipped — no guessing.** On any hard/uncertain/high-stakes decision,
   an agent must run the concert mini-loop (below) instead of picking the first idea.
7. **Adversarial gate before "done."** Nothing ships until a skeptic told to *refute by default*
   fails to break it. (from /concert §verify)

## Concert protocol embedded in EVERY agent
Paste this block into every agent prompt you spawn. It makes each team member behave like a
mini-consortium instead of a lone guesser:

> CONCERT DISCIPLINE — when you face a hard call (≥1 plausible alternative, or being wrong is
> expensive): do NOT commit to the first option. (a) GROUND in the real artifacts you were given.
> (b) Enumerate 3–5 distinct candidate approaches — different mechanisms, not rewordings.
> (c) Compare them head-to-head: mechanism, fit-to-exact-facts, risk/blast-radius, effort,
> confidence-it-works. (d) Pick the winner by (probability it works) × (low risk), and name the
> cheapest decisive test that would confirm it. (e) Self-adversary: try to REFUTE your pick —
> would it actually work on the exact condition, could it regress anything? Only then commit, and
> report the comparison, not just the answer. For a PIVOTAL fork above your pay grade, stop and
> hand the orchestrator a flagged decision so it can convene a full `/concert` workflow.

(The orchestrator — you — CAN convene a real `/concert` for the mission's biggest forks, since
nested workflows are one level deep: run concert at the top, then the execution team below.)

## Operating procedure
1. **Ground** — assemble `CONTEXT` from real artifacts (§law 1).
2. **Plan** — decompose into a role graph. Default roles (scale up/down to stakes):
   - **Scout** — research/recon (parallel, one per unknown angle; concert-disciplined).
   - **Architect** — turns scout findings + CONTEXT into a concrete plan with data contracts.
   - **Builders** — implement independent slices (parallel, worktree-isolated if they touch files).
   - **Verifier** — adversarial skeptic per deliverable, refute-by-default.
   - **Integrator** — merges, resolves conflicts, runs the final adversarial gate.
   For genuinely uncertain *approach* decisions, insert a real `/concert` before Architect.
3. **Run the Workflow** (template below): a PIPELINE so each slice flows scout→build→verify
   without waiting on the slowest peer; barriers only where a stage genuinely needs all prior
   results (e.g. integrate).
4. **Cap agency** — give each agent explicit turn limits + a tight scope. *"Unlimited agency makes
   agents search exhaustively and waste tokens."* (/everything)
5. **Classify failures** — on tool errors, bucket into {bad args, bad environment, provider error}
   and tune the harness; *"10× error reduction on the same model by fixing the harness."* (/everything ★)
6. **Integrate + gate** — only declare done after the adversarial verifier fails to refute.

## Workflow template (adapt roles, schemas, counts, models to the mission)
```js
export const meta = {
  name: 'vishnu-<mission-slug>',
  description: '<one line: what this team ships>',
  phases: [
    { title: 'Scout',     detail: 'parallel recon, one agent per independent unknown' },
    { title: 'Architect', detail: 'merge recon into a contract-bound plan' },
    { title: 'Build',     detail: 'parallel builders on independent slices (worktree-isolated)' },
    { title: 'Verify',    detail: 'adversarial skeptic per deliverable' },
    { title: 'Integrate', detail: 'merge + final refute-by-default gate' },
  ],
}

const CONTEXT = `...REAL grounded facts: paths, versions, exact requirements, constraints...`
const CONCERT = `CONCERT DISCIPLINE — <paste the embedded block above>`

// ---- Scout: parallel recon on independent angles (diverse model tiers = independent views)
phase('Scout')
const PANEL = ['opus','sonnet','haiku']; const pick = i => ({ model: PANEL[i % PANEL.length] })
const angles = [ /* one entry per independent unknown */ ]
const RECON = { type:'object', additionalProperties:false, required:['findings','risks'],
  properties:{ findings:{type:'array',items:{type:'string'}}, risks:{type:'array',items:{type:'string'}} } }
const recon = (await parallel(angles.map((a,i)=>()=>
  agent(`${a.q}\n\n${CONCERT}\n\n=== CONTEXT ===\n${CONTEXT}`,
        {label:`scout:${a.key}`, phase:'Scout', schema:RECON, ...pick(i)})))).filter(Boolean)

// ---- Architect: one plan with explicit data contracts + independent vs serial slices
phase('Architect')
const PLAN = { type:'object', additionalProperties:false, required:['slices'],
  properties:{ slices:{type:'array',items:{ type:'object', additionalProperties:false,
    required:['id','goal','independent','contract'],
    properties:{ id:{type:'string'}, goal:{type:'string'},
      independent:{type:'boolean'}, contract:{type:'string'} } } } } }
const plan = await agent(
  `You are the ARCHITECT. Turn the recon + CONTEXT into a build plan of slices. Mark each slice `
  +`independent:true ONLY if it shares no files/state with another. Define each slice's output `
  +`contract.\n\nRECON:\n${JSON.stringify(recon)}\n\n${CONCERT}\n\n${CONTEXT}`,
  {label:'architect', phase:'Architect', schema:PLAN})

// ---- Build→Verify as a PIPELINE per slice (no barrier). Worktree-isolate file mutators.
const RESULT = { type:'object', additionalProperties:false, required:['summary','artifacts','selfTest'],
  properties:{ summary:{type:'string'}, artifacts:{type:'array',items:{type:'string'}}, selfTest:{type:'string'} } }
const VERDICT = { type:'object', additionalProperties:false, required:['passes','reason','fix'],
  properties:{ passes:{type:'boolean'}, reason:{type:'string'}, fix:{type:'string'} } }
const built = await pipeline(plan.slices,
  (s)=> agent(`BUILD slice "${s.id}": ${s.goal}. Honor contract: ${s.contract}.\n${CONCERT}\n\n${CONTEXT}`,
        {label:`build:${s.id}`, phase:'Build', schema:RESULT, ...(s.independent?{isolation:'worktree'}:{})}),
  (res, s)=> agent(`Adversarially verify slice "${s.id}". REFUTE BY DEFAULT: does it meet the `
        +`contract (${s.contract}) and could it regress anything? \nRESULT:\n${JSON.stringify(res)}\n\n${CONTEXT}`,
        {label:`verify:${s.id}`, phase:'Verify', schema:VERDICT})
        .then(v=>({slice:s.id, res, v})))

// ---- Integrate: barrier (needs all slices) + final adversarial gate
phase('Integrate')
const passing = built.filter(Boolean).filter(b=>b.v?.passes)
const integration = await agent(
  `You are the INTEGRATOR. Merge these verified slices into one coherent deliverable; resolve `
  +`conflicts; then run a FINAL refute-by-default check on the whole. List anything still unproven.\n`
  +`SLICES:\n${JSON.stringify(passing)}\n\n${CONTEXT}`,
  {label:'integrate', phase:'Integrate', schema:{ type:'object', additionalProperties:false,
    required:['shipIt','deliverable','openRisks'],
    properties:{ shipIt:{type:'boolean'}, deliverable:{type:'string'}, openRisks:{type:'array',items:{type:'string'}} } }})
return { plan, built, integration }
```

## Scaling to stakes (speed knob)
- **Quick rip** — 2–3 scouts, 1 architect, 2 builders, 1 verifier. Minutes.
- **All-out** — 6–8 scouts across model tiers, a real `/concert` on the approach, N parallel
  worktree builders, a verifier per slice + a cross-model final adversary.
- Always: parallel the independent, serial the shared, contract every handoff, gate on the adversary.

## What makes this "Fable-5-but-better"
Not a bigger model — a **harder harness**. /vishnu wraps whatever model it runs on in grounding,
a no-guess concert reflex, context-isolated parallelism, contract-checked handoffs, and an
adversarial gate. Per the corpus, that harness craft is exactly what turns a given model from
45%→55% — applied team-wide, it lets the crew punch far above any single agent.

## Self-improvement loop (guarded — never skip the guard)
/vishnu can harden /everything (and itself) on a loop, SAFELY. Each iteration:
1. **Snapshot** — `python3 <pipeline>/guard.py --snapshot` → SNAP (backs up every global skill + metrics).
2. **Audit** — `python3 <pipeline>/adapt.py --audit` for branch health (now relative/percentile, so it
   actually flags weak branches), or run a vishnu audit workflow for deeper structural findings.
3. **Apply only adversarially-survived improvements.** Prefer SAFE actions: `adapt.py --improve <branch>`
   (non-regressive — refuses to write if ★/confidence would drop) and `adapt.py --enrich <branch>` →
   distill those videos → `build_skilltree.py --install`. Do NOT edit pipeline code unattended.
4. **Verify** — `python3 <pipeline>/guard.py --verify --against SNAP`. Auto-rolls back if total points/★
   drop, any branch is gutted (>40%), or validation fails. Cross-branch redistribution is allowed.
5. **Log + repeat** until 2 consecutive iterations produce no kept gain (stall), then stop.
The guard is what makes self-editing safe: nothing survives that regresses the tree.

## Honesty clause (inherited from /concert)
Always surface the comparison and the open risks, including "this may not be doable as asked."
Speed is for the work, never for skipping the adversarial gate.
