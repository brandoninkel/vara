#!/usr/bin/env python3
"""
Pack the corpus into size-bounded batches for the Haiku distill fleet.

Why batches: a single Workflow caps at 1000 agents lifetime, but the sweep
yields thousands of videos. So we pack several small videos per agent (under a
word budget) and give huge transcripts (e.g. Karpathy 40k words) their own
batch. Each batch -> one Haiku agent.

Output: pipeline/batches.json  ->  [{ "batch": i, "ids": [...], "words": N }, ...]
Pass this to the distill workflow via `args`.
"""
import argparse, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--word-budget", type=int, default=32000,
                    help="max transcript words packed into one agent/batch")
    ap.add_argument("--min-words", type=int, default=120,
                    help="skip videos with fewer transcript words (intros/teasers)")
    ap.add_argument("--out", default=os.path.join(HERE, "batches.json"))
    args = ap.parse_args()

    files = [f for f in glob.glob(os.path.join(CORPUS, "*.json"))
             if not f.endswith("corpus.jsonl")]
    vids = []
    skipped_short = skipped_nocap = 0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        w = d.get("transcript_words") or 0
        if not d.get("has_captions"):
            skipped_nocap += 1
            continue
        if w < args.min_words:
            skipped_short += 1
            continue
        vids.append((d["id"], w))

    # biggest first; a video over budget gets its own (oversized) batch
    vids.sort(key=lambda x: -x[1])
    batches, cur, cur_w = [], [], 0
    for vid, w in vids:
        if w >= args.word_budget:
            batches.append([(vid, w)])
            continue
        if cur_w + w > args.word_budget and cur:
            batches.append(cur)
            cur, cur_w = [], 0
        cur.append((vid, w))
        cur_w += w
    if cur:
        batches.append(cur)

    out = [{"batch": i, "ids": [v for v, _ in b], "words": sum(w for _, w in b)}
           for i, b in enumerate(batches)]
    json.dump(out, open(args.out, "w"), indent=0)
    tot_w = sum(b["words"] for b in out)
    print(f"corpus files: {len(files)}  usable videos: {len(vids)}  "
          f"(skipped {skipped_short} short, {skipped_nocap} no-caption)")
    print(f"batches: {len(out)}  total words: {tot_w:,}  "
          f"avg/batch: {tot_w//max(1,len(out)):,}")
    print(f"-> {args.out}  (pass as Workflow args)")
    if len(out) > 1000:
        print(f"WARNING: {len(out)} batches > 1000-agent workflow cap. "
              f"Raise --word-budget or split across workflows.")


if __name__ == "__main__":
    main()
