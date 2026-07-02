#!/usr/bin/env python3
"""Quick local analysis of the transcript corpus — what's actually in here."""
import json, glob, re, collections

files = [f for f in glob.glob("corpus/*.json") if not f.endswith("corpus.jsonl")]
recs = []
for f in files:
    try:
        recs.append(json.load(open(f, encoding="utf-8")))
    except Exception:
        pass
recs = [r for r in recs if r.get("has_captions")]

tot_w = sum(r.get("transcript_words", 0) for r in recs)
print(f"== CORPUS ==  {len(recs)} videos · {tot_w:,} words · {tot_w*1.3/1e6:.1f}M tokens (approx)")

# by channel
ch = collections.Counter()
chw = collections.Counter()
for r in recs:
    ch[r.get("channel") or "?"] += 1
    chw[r.get("channel") or "?"] += r.get("transcript_words", 0)
print("\n== TOP CHANNELS (videos / words) ==")
for c, n in ch.most_common(15):
    print(f"  {c[:30]:<31}{n:>4} vids  {chw[c]:>11,} w")

# recency
yr = collections.Counter(str(r.get("upload_date") or "")[:4] for r in recs)
print("\n== BY YEAR ==", "  ".join(f"{y}:{n}" for y, n in sorted(yr.items()) if y))

# term frequency — the vocabulary of the field
TERMS = {
    "agents/agentic": r"\bagent(s|ic)?\b", "Claude Code": r"claude code",
    "MCP": r"\bmcp\b|model context protocol", "subagents": r"sub-?agent",
    "skills": r"\bskills?\b", "harness": r"\bharness", "evals": r"\beval(s|uation)?\b",
    "rubric": r"rubric", "RAG/retrieval": r"\brag\b|retrieval", "embeddings": r"embedding",
    "vector db": r"vector (db|database|store)", "fine-tuning": r"fine[- ]?tun",
    "RLHF": r"\brlhf\b|reinforcement learning from", "prompt eng": r"prompt(ing| engineering)?",
    "context window": r"context window", "context engineering": r"context engineering",
    "compaction": r"compact", "tool use": r"tool (use|calling)|function calling",
    "multi-agent": r"multi[- ]?agent", "orchestration": r"orchestrat",
    "chain-of-thought": r"chain of thought|reasoning model", "hallucination": r"hallucinat",
    "observability/tracing": r"observability|tracing|\btraces?\b", "guardrails": r"guardrail",
    "vibe coding": r"vibe cod", "Cursor": r"\bcursor\b", "Copilot": r"copilot",
    "LangChain/Graph": r"langchain|langgraph", "transformer": r"transformer|attention",
    "diffusion": r"diffusion", "deployment/prod": r"\bdeploy|production",
}
vids_with = collections.Counter()
total_hits = collections.Counter()
for r in recs:
    t = (r.get("transcript") or "").lower()
    for name, pat in TERMS.items():
        h = len(re.findall(pat, t))
        if h:
            vids_with[name] += 1
            total_hits[name] += h
print("\n== FIELD VOCABULARY (videos mentioning / total mentions) ==")
for name in sorted(TERMS, key=lambda k: -vids_with[k]):
    bar = "█" * (vids_with[name] * 40 // max(1, len(recs)))
    print(f"  {name:<22}{vids_with[name]:>4} vids {total_hits[name]:>6} hits  {bar}")

# top by views
print("\n== TOP 12 BY VIEWS ==")
for r in sorted(recs, key=lambda r: -(r.get("view_count") or 0))[:12]:
    print(f"  {(r.get('view_count') or 0):>11,}  {(r.get('channel') or '')[:18]:<18} {(r.get('title') or '')[:50]}")
