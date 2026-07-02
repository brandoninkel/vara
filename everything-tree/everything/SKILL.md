---
name: everything
description: Primary orchestrator of a SELF-IMPROVING AI skill tree distilled from ~1900 top AI YouTube lectures, conference talks and agentic-coding channels (Karpathy, Anthropic, AI Engineer, DeepMind, Stanford, research + builder creators). Use when the user asks anything about building with AI, LLMs, agents, agent skills, Claude Code, prompting, RAG, fine-tuning, evals, harness design, ML foundations, or the AI landscape. Routes to everything-<domain> sub-skills AND adapts the tree to fix its own weaknesses.
---

# /everything — Self-Improving AI Skill Tree

_Built 2026-06-19 from 1756 videos → 14577 raw claims → 14014 vetted, deduped, trust-ranked points across 16 branches._

## How to use this orchestrator

1. Identify which domain(s) the user's question touches (branch list below).
2. Invoke the matching `everything-<domain>` sub-skill(s) via the Skill tool to load that branch's distilled knowledge.
3. Answer grounded in those points. Prefer ★ (multi-source corroborated) points; treat ⚠️ disputed points with caution. Cite the source channel for load-bearing claims.

## ⟳ Self-adaptation protocol — RUN EVERY INVOCATION (hardcoded, non-optional)

This tree is self-learning: it MUST get stronger every time it is used. On EVERY invocation, after answering, you MUST run the adaptation loop:

1. **Audit** — read each branch's health from its `everything-<domain>/report.json` (this pack ships the tree WITHOUT the distill pipeline; if `adapt.py` from the vara distill pipeline is installed on this machine, `adapt.py --audit` automates this) (points, avg confidence, multi-source %, weak flags) gathered from every `everything-*/report.json`.
2. **Detect weakness** in the branch(es) you just used. A branch is WEAK if any hold: it had NO point relevant to the task; the best point was low-confidence (<0.6) or ⚠️ disputed; the audit flags the branch `weak`; or you had to answer from your own knowledge because the branch lacked coverage.
3. **Improve** — for each weak branch D: if the gap is a specific correct fact you just established, append it as a new point to `everything-D/SKILL.md` and update its `report.json`. (Re-mining/enriching branches requires the vara distill pipeline + claims corpus, which this pack does not include — without it, treat the tree as expert static knowledge and log gaps instead.)
4. **Log** — append one line to `_adaptation_log.md` (beside these skills): what branch, what weakness, what action.
5. **Never skip steps 2–4.** Strengthening the tree is part of answering, not optional.

## Branches (with live health)

- **everything-prompting** — 1099 pts, 24 ★multi-src, conf 0.77 ✅. prompting.
- **everything-agents** — 2719 pts, 115 ★multi-src, conf 0.81 ✅. agents.
- **everything-agentic-coding** — 2573 pts, 56 ★multi-src, conf 0.81 ✅. agentic coding.
- **everything-rag** — 463 pts, 6 ★multi-src, conf 0.81 ✅. rag.
- **everything-llm-internals** — 414 pts, 6 ★multi-src, conf 0.82 ✅. llm internals.
- **everything-finetuning** — 99 pts, 2 ★multi-src, conf 0.82 ✅. finetuning.
- **everything-evals** — 640 pts, 4 ★multi-src, conf 0.83 ✅. evals.
- **everything-model-landscape** — 949 pts, 19 ★multi-src, conf 0.78 ✅. model landscape.
- **everything-inference-serving** — 671 pts, 4 ★multi-src, conf 0.82 ✅. inference serving.
- **everything-data-curation** — 197 pts, 0 ★multi-src, conf 0.82 ✅. data curation.
- **everything-ml-foundations** — 174 pts, 0 ★multi-src, conf 0.84 ✅. ml foundations.
- **everything-ai-products** — 2257 pts, 41 ★multi-src, conf 0.77 ✅. ai products.
- **everything-safety-alignment** — 535 pts, 0 ★multi-src, conf 0.82 ✅. safety alignment.
- **everything-automation** — 623 pts, 3 ★multi-src, conf 0.81 ✅. automation.
- **everything-research-frontiers** — 298 pts, 2 ★multi-src, conf 0.76 ✅. research frontiers.
- **everything-career-learning** — 303 pts, 0 ★multi-src, conf 0.78 ✅. career learning.

## Trust model (the bullshit meter, transcript-era)

Comments were rate-limited out, so trust = ① cross-source corroboration (same point from N independent channels → ★), ② channel authority tier (Karpathy/Anthropic/AI Engineer/DeepMind weighted up), ③ recency (2026 > 2024), ④ view/like engagement. Disputed/low-trust points are dropped or flagged ⚠️.

## Pipeline (for --enrich / full refresh)

This pack ships the built tree only. Full refresh (ingest → distill → rebuild) requires the vara distill pipeline (not included).