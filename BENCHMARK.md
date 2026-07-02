# Vara self-improvement loop — final benchmark report

**Verdict: vara works, and the loop measurably improved it — v1.1.0 → v1.1.3 over 6 bench
iterations (~7M subagent tokens, ~190 agents), every edit evidence-driven and guard-protected.**

## Final lift numbers (vara-driven minus bare, same model, same 3 tasks, 0–10 scale)

| Model | pre-loop (it1, v1.1.0) | post-loop (v1.1.3) | confidence |
|---|---|---|---|
| **sonnet** | +0.17 | **≈ +0.5** (0.46 / 0.66 replicated; 4 straight positives) | HIGH — stable across every run |
| **haiku** | **−0.47** (vara HURT) | **+0.69 two-run mean** (+1.55 / −0.18) | MODERATE — direction clearly fixed, magnitude high-variance |
| **opus** | — | **+0.47** (single read) | no high-tier regression; vara helps even the strong tier |

## Lift curve
```
        it1     it2     it3     it4     it5
haiku  -0.47   -0.03   -0.06   +1.55   -0.18     edits: v1.1.1↑        v1.1.3↑  (replication)
sonnet +0.17   +0.55   +0.48   +0.46   +0.66
opus     —       —     +0.47     —       —
```

## What the loop learned (each from judge-diagnosed evidence, not vibes)
1. **v1.1.1 — "Deliverables are FILES, not chat"** (D5): drivers kept proof in their final
   message; the graded workspace got nothing. Effect: haiku +0.44, sonnet +0.38. KEPT.
2. **v1.1.2 — "The spec is law at the gate"** (D7, prose): no measurable effect — haiku still
   wrote a false "verified correct" the very next run. KEPT (zero-cost) but the lesson is the
   headline: **prose admonitions don't move small models.**
3. **v1.1.3 — "The gate is an ARTIFACT"** (GATE.md: requirement / command / PASS-FAIL rows):
   haiku swept all 3 tasks the first run (+1.55), incl. fixing the exact spec-edge bug it had
   twice botched, with an honest gate matrix. Replication regressed to −0.18 (compliance
   variance), two-run mean +0.69. KEPT.

**The core discovery: artifact-forcing beats doctrine-preaching.** Both big wins came from
rules that force the driver to produce a FILE (proof files, gate matrix) rather than hold an
intention. When haiku complies with the artifacts, it beats bare-haiku decisively; its
residual variance is compliance, not capability.

## Instrument notes (iteration 0 was spent fixing the ruler)
- it0 exposed judge noise (identical files scored 9 vs 7.25) → 2-judge blind panel, averaged,
  must-agree-else-tie, rationale fields mandatory.
- Objective ceiling (all arms passed all hidden tests) → hardened to 6 hidden tests/task.
- Protocol amendments logged in LOOP.md (noise band ±0.15; final replication run). All raw
  data: bench_log.jsonl, runs/it0–it5, judge rationales in each workflow result.

## Honest limits
- n=1 per cell per iteration; haiku numbers swing ±1.5. Means quoted over replications.
- Vara arm = solo-emulated doctrine (no nested fleets) — measures the shareable skill text,
  not the full team harness (which routes verification to strong models and should only widen
  the gap).
- 3 tasks, one domain family (code+decision). Broader task diversity = future work.

## Deployed
v1.1.3 is live at ~/.claude/skills/vara (guard-verified at every step) and synced to the
public repo. The loop is stopped; rerun anytime: `LOOP.md` has the full protocol.
