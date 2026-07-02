#!/usr/bin/env python3
"""Pick ~18 high-value target videos for a distill pilot; write pilot_batches.json."""
import json, glob, re, os

TARGET = re.compile(r"agent|claude code|skill|mcp|eval|harness|context|subagent|"
                    r"prompt|rag|orchestrat|llm|reproduce|build", re.I)
TRUST = {"Andrej Karpathy", "Anthropic", "AI Engineer", "DeepLearningAI",
         "Latent Space", "Cognition", "IndyDevDan", "Cole Medin", "Sam Witteveen"}

recs = []
for f in glob.glob("corpus/*.json"):
    if f.endswith("corpus.jsonl"):
        continue
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not d.get("has_captions"):
        continue
    w = d.get("transcript_words") or 0
    if not (400 <= w <= 30000):          # skip teasers + 4hr monsters for the pilot
        continue
    if (d.get("channel") in TRUST) and TARGET.search(d.get("title") or ""):
        recs.append(d)

# best by views, diversify channels
recs.sort(key=lambda r: -(r.get("view_count") or 0))
picked, seen_ch = [], {}
for r in recs:
    c = r.get("channel")
    if seen_ch.get(c, 0) >= 3:           # max 3 per channel in pilot
        continue
    seen_ch[c] = seen_ch.get(c, 0) + 1
    picked.append(r)
    if len(picked) >= 18:
        break

# pack into <=32k-word batches
picked.sort(key=lambda r: -(r.get("transcript_words") or 0))
batches, cur, cw = [], [], 0
for r in picked:
    w = r.get("transcript_words") or 0
    if cw + w > 32000 and cur:
        batches.append(cur); cur, cw = [], 0
    cur.append((r["id"], w)); cw += w
if cur:
    batches.append(cur)
out = [{"batch": i, "ids": [v for v, _ in b], "words": sum(w for _, w in b)}
       for i, b in enumerate(batches)]
json.dump(out, open("pipeline/pilot_batches.json", "w"))
print(f"pilot: {len(picked)} videos -> {len(out)} batches")
for r in picked:
    print(f"  {(r.get('view_count') or 0):>10,} {(r.get('channel') or '')[:16]:<16} {(r.get('title') or '')[:52]}")
