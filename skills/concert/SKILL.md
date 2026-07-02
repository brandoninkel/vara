---
name: concert
description: >-
  Run a CONSORTIUM of subagents to research and COMPARE solutions before deciding —
  parallel multi-angle research → ranked comparison matrix → adversarial verification →
  a single compared, evidence-backed recommendation. Use for any hard, uncertain, or
  high-stakes problem where a wrong guess is expensive: a stubborn bug that survived
  multiple fixes, an architecture/library/approach choice, a tricky diagnosis, or any
  time the user says "concert", "consortium", "compare options", "don't guess", or
  "research and compare before deciding". The skill IS the opt-in to use the Workflow tool.
---

# concert — a consortium that compares before it commits

When invoked, you orchestrate a panel of subagents (a "concert") that **researches multiple
angles in parallel, compares the candidate solutions head-to-head, and adversarially
verifies the front-runner — then hands back ONE compared, evidence-backed recommendation.**
You do **not** apply a fix until the comparison is on the table. This is the antidote to
serial guessing: instead of trying fix → deploy → see-if-it-works → repeat, you generate
and weigh the options first.

`$ARGUMENTS` (or the surrounding conversation) is the problem to run the concert on.

## When to use it
- A bug that already survived ≥1 fix attempt, or where you can't reproduce it locally.
- Choosing between approaches/libraries/architectures with real trade-offs.
- Any decision where being wrong costs a deploy cycle, a native rebuild, user trust, or hours.
- The user explicitly asks for a consortium / "compare before you decide".

## When NOT to use it
- A one-line obvious fix, or something already verified. Don't convene a panel to change a
  constant. Solo it.

## Method (do these in order)

### 1. Frame + GROUND the problem (do this yourself, first — cheaply)
A consortium reasoning over generic knowledge is worthless. Before spawning anyone, gather
the **real artifacts** so every agent argues from facts, not vibes:
- Read the actual code/config/logs/error output involved (Grep/Read/Bash). Quote exact
  symptoms, versions, line numbers, and what's *already been tried and failed*.
- State the observable facts precisely (e.g. "stream live, rs=4, element connected, yet
  preview black; iPad fine, iPhone black; fixes A,B,C already failed").
- Build one `CONTEXT` string with all of this. It gets embedded in every agent's prompt.

### 2. Decompose into independent ANGLES
Split the problem into 3–8 angles that don't overlap — different hypotheses, layers, or
failure modes (e.g. for a bug: OS/platform regression, a CSS/ancestor cause, a config cause,
a timing/lifecycle cause). For a decision: each candidate approach is an angle, plus a
"what breaks each" angle. List them before writing the script.

### 3. Run the Workflow (research → compare → verify)
Author and run a `Workflow` with three phases (adapt the template below). Scale the panel to
the stakes: **quick** = 3 research + 1 compare + 1 verify; **hard/high-stakes** = 6–8 research
+ 1 compare-per-subproblem + 1 verify-per-top-recommendation. Each research agent returns
**structured** candidate solutions with mechanism, fit-to-the-exact-symptoms, confidence, and
evidence URLs. The compare agent must produce a **ranked matrix** (option, exact change,
pros, cons, risk to other surfaces, effort, confidence-it-fixes-it) + a single
`topRecommendation` + the **cheapest decisive test** to run before committing. The verify
agent is an adversary told to **refute by default**.

### 4. Present the comparison, then decide WITH the user
Report back: the ranked options, the recommended path and *why it beats the alternatives*,
the adversary's caveats (state them honestly — including "this might be unfixable from our
side"), and the cheapest decisive experiment. **Do not silently apply a fix.** If one option
is clearly dominant and low-risk, say so and proceed; if it hinges on an unknown, run the
decisive test (or ask the user to) first.

## Template (adapt — names, angles, schemas, agent counts)

```js
export const meta = {
  name: 'concert-<short-slug>',
  description: '<one line: what this concert decides>',
  phases: [
    { title: 'Research', detail: 'N parallel agents, one per angle' },
    { title: 'Compare', detail: 'ranked comparison matrix + recommendation' },
    { title: 'Verify', detail: 'adversarial skeptic on the front-runner(s)' },
  ],
}

// 1) the grounded context — REAL facts, versions, symptoms, what already failed
const CONTEXT = `...paste the concrete, factual problem brief here...`

const FINDINGS = {
  type: 'object', additionalProperties: false,
  required: ['solutions', 'sources'],
  properties: {
    keyFinding: { type: 'string' },
    solutions: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      required: ['approach', 'mechanism', 'fitsTheExactSymptoms', 'confidence', 'evidenceUrls'],
      properties: {
        approach: { type: 'string' },
        mechanism: { type: 'string' },
        fitsTheExactSymptoms: { type: 'string' }, // must cite OUR specifics, not generic theory
        confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        evidenceUrls: { type: 'array', items: { type: 'string' } },
      },
    }},
    sources: { type: 'array', items: { type: 'string' } },
  },
}

phase('Research')
const angles = [
  { key: 'angle-a', q: 'Research <hypothesis/approach A>. Does it fit OUR exact symptoms? ...' },
  { key: 'angle-b', q: 'Research <hypothesis/approach B>. ...' },
  // ...3–8 total, each a distinct, non-overlapping lens
]
// A CONSORTIUM OF MODELS: optionally rotate the panel across model tiers so you get
// genuinely independent reasoning, not one model answering N times. Omit `model` to inherit
// the session model — that's the safe default, and diverse ANGLES matter more than diverse
// weights — but spreading tiers adds real perspective diversity, and (below) putting the
// adversary on a DIFFERENT model than the synthesizer keeps it from sharing blind spots.
const PANEL = ['opus', 'sonnet', 'haiku'] // set to [] / omit `model` to keep one model
const pick = (i) => (PANEL.length ? { model: PANEL[i % PANEL.length] } : {})
const research = await parallel(angles.map((a, i) => () =>
  agent(`${a.q}\n\n=== CONTEXT ===\n${CONTEXT}`, { label: `research:${a.key}`, phase: 'Research', schema: FINDINGS, ...pick(i) })
))

phase('Compare')
const COMPARE = {
  type: 'object', additionalProperties: false,
  required: ['rootCauseOrCriteria', 'rankedOptions', 'topRecommendation', 'cheapestDecisiveTest'],
  properties: {
    rootCauseOrCriteria: { type: 'string' }, // best theory of cause, or the decision criteria
    rankedOptions: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      required: ['rank', 'option', 'exactChange', 'pros', 'cons', 'risk', 'effort', 'confidenceItWorks'],
      properties: {
        rank: { type: 'number' },
        option: { type: 'string' },
        exactChange: { type: 'string' }, // precise enough to implement
        pros: { type: 'string' }, cons: { type: 'string' },
        risk: { type: 'string' }, // blast radius to other surfaces/users
        effort: { type: 'string', enum: ['trivial', 'small', 'medium', 'large'] },
        confidenceItWorks: { type: 'string', enum: ['high', 'medium', 'low'] },
      },
    }},
    topRecommendation: { type: 'string' }, // and WHY it beats the runners-up
    cheapestDecisiveTest: { type: 'string' }, // the experiment that confirms the cause/choice before committing
  },
}
const comparison = await agent(
  `You are the LEAD. Merge these research dossiers into a RANKED comparison + one recommendation. `
  + `Be decisive about the most likely actual cause / best choice; rank by (probability it works) × (low risk). `
  + `Mark which options are stackable, and give the cheapest decisive test to run BEFORE committing.\n\n`
  + `DOSSIERS:\n${JSON.stringify(research.map((r, i) => ({ angle: angles[i].key, ...r })), null, 2)}\n\n${CONTEXT}`,
  { label: 'compare', phase: 'Compare', schema: COMPARE })

phase('Verify')
const VERDICT = {
  type: 'object', additionalProperties: false,
  required: ['survives', 'reason', 'refinedChange'],
  properties: {
    survives: { type: 'boolean' },
    reason: { type: 'string' },       // would it ACTUALLY work? regressions? be a skeptic
    refinedChange: { type: 'string' }, // tightened change, or '' if it stands
  },
}
const adversarial = await agent(
  `Adversarially verify the top recommendation. Default to REFUTE: would it actually work on the `
  + `exact reported condition, and could it regress anything? Verify every load-bearing claim. If sound, tighten it.\n\n`
  + `RECOMMENDATION:\n${JSON.stringify(comparison, null, 2)}\n\n${CONTEXT}`,
  // Cross-model adversary: put the skeptic on a DIFFERENT model than the synthesizer so it
  // doesn't inherit the same blind spots (omit `model` on the compare agent above, set one here).
  { label: 'verify', phase: 'Verify', schema: VERDICT, ...(PANEL.length ? { model: PANEL[0] } : {}) })

return { comparison, adversarial }
```

For multi-part problems (e.g. two independent bugs at once), run a compare+verify pair PER
sub-problem (see the camera+session split that birthed this skill): give each its own slice of
the research dossiers, its own `COMPARE`, and its own adversary.

## Principles (what makes a concert better than one model guessing)
- **A consortium of MODELS, not one model N times.** The point is independent perspectives:
  diverse *angles* first (the big lever), and optionally diverse *model tiers* across the panel
  with a **cross-model adversary** so the skeptic doesn't share the proposer's blind spots.
- **Domain-agnostic.** Nothing here is tied to one codebase or problem type — the same
  ground → decompose → research → compare → verify loop runs on a bug, a library choice, an
  architecture call, a data question, or a research prompt. Swap the angles and the schema.
- **Diversity beats redundancy.** Each angle is a *different* lens; don't spawn N agents asking
  the same question. The value is in disagreement surfacing what one view misses.
- **Ground everything in real artifacts.** Cite OUR files/versions/symptoms; reject generic answers.
- **Adversarial gate.** The front-runner must survive a skeptic told to refute it — that's what
  catches the plausible-but-wrong fix before it ships.
- **Compare, then decide.** Always show the ranked trade-offs and the cheapest decisive test
  before applying anything. Honesty includes "this may be unfixable from our side."
- **Scale to stakes.** A quick question gets a trio; a trust-eroding, multiply-failed bug gets
  the full panel.
