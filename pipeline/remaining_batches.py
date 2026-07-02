#!/usr/bin/env python3
"""Compute batches still needing distillation (videos with no claims/<id>.json yet)."""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLAIMS = os.path.join(ROOT, "claims")

batches = json.load(open(os.path.join(HERE, "batches.json")))
done = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(CLAIMS, "*.json"))}

remaining = []
for b in batches:
    missing = [i for i in b["ids"] if i not in done]
    if missing:
        remaining.append({"batch": len(remaining), "ids": missing, "words": b.get("words", 0)})

json.dump(remaining, open(os.path.join(HERE, "batches_remaining.json"), "w"))
tot_ids = sum(len(b["ids"]) for b in batches)
rem_ids = sum(len(b["ids"]) for b in remaining)
print(f"total videos: {tot_ids}  distilled: {len(done)}  remaining: {rem_ids}")
print(f"remaining batches: {len(remaining)} -> pipeline/batches_remaining.json")
