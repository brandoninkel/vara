#!/usr/bin/env python3
"""
Self-adaptation tool for the /everything tree. The orchestrator runs this on
every invocation to find and fix weak branches.

  adapt.py --audit                      # health of every branch (reads report.json)
  adapt.py --improve agents             # re-mine+re-rank one branch from full claims (local, always works)
  adapt.py --enrich agents              # list undistilled corpus videos for a branch (feed a re-distill)
  adapt.py --rebuild                    # regenerate the whole tree from claims

Flags: --tree <dir> (default ~/.claude/skills), --claims-dir <dir>.
"""
import argparse, json, glob, os, re, sys, datetime
import build_skilltree as bst   # reuse the builder's logic

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DOMAIN_KW = {
    "prompting": r"prompt|context window|system prompt|few.?shot",
    "agents": r"\bagent|agentic|tool use|multi.?agent|orchestrat",
    "agentic-coding": r"claude code|cursor|copilot|vibe cod|coding agent|hooks|sub.?agent",
    "rag": r"\brag\b|retrieval|embedding|vector",
    "llm-internals": r"transformer|attention|token|architecture|backprop",
    "finetuning": r"fine.?tun|lora|rlhf|distill",
    "evals": r"\beval|benchmark|rubric|llm.as.a.judge",
    "model-landscape": r"gpt|claude|gemini|llama|model release|frontier",
    "inference-serving": r"inference|serving|vllm|quantiz|latency|throughput|deploy",
    "data-curation": r"dataset|synthetic data|data quality|curation",
    "ml-foundations": r"gradient|neural net|statistics|regression|probability",
    "ai-products": r"product|startup|user|business|monetiz",
    "safety-alignment": r"alignment|safety|interpretab|jailbreak|guardrail",
    "automation": r"\bn8n|make\.com|zapier|workflow automation|no.?code",
    "research-frontiers": r"paper|sota|state of the art|novel|research",
    "career-learning": r"learn|career|roadmap|beginner|how to start",
}


def audit(tree):
    reps = []
    for d in sorted(glob.glob(os.path.join(tree, "everything-*"))):
        rp = os.path.join(d, "report.json")
        if os.path.exists(rp):
            try:
                reps.append(json.load(open(rp)))
            except Exception:
                pass
    if not reps:
        print(f"no report.json under {tree} (build the tree first)"); return []
    # RELATIVE weak detection — the absolute <25-pt floor in build never fires (smallest
    # branch is ~99), so weakness must be judged against the rest of the tree.
    pts = sorted(r["points"] for r in reps)
    p25 = pts[max(0, len(pts) // 4 - 1)]
    conf_lo = sorted(r["avg_confidence"] for r in reps)[max(0, len(reps) // 4 - 1)]
    print(f"== /everything health ({tree}) ==  (p25 size={p25})")
    print(f"{'branch':<28}{'pts':>5}{'★%':>6}{'conf':>6}  status")
    weak = []
    for r in sorted(reps, key=lambda r: r["points"]):
        flags = list(r.get("weak") or [])
        if r["points"] <= p25:
            flags.append(f"bottom-quartile size")
        if r["points"] >= 50 and r["multi_source_pct"] == 0:
            flags.append("0% cross-source ★")
        if r["avg_confidence"] <= conf_lo:
            flags.append("low-quartile confidence")
        st = "⚠️ " + "; ".join(flags) if flags else "✅"
        if flags:
            weak.append(r["domain"])
        print(f"  {r['skill']:<26}{r['points']:>5}{int(r['multi_source_pct']*100):>5}%"
              f"{r['avg_confidence']:>6}  {st}")
    print(f"\nweak branches ({len(weak)}): {weak or 'none'}")
    return weak


def improve(domain, tree, claims_dir):
    """Re-mine + re-rank ONE branch from the full claim set with relaxed thresholds."""
    bst.load_corpus_meta()
    claims = [c for c in bst.load_claims(claims_dir) if c.get("domain") == domain]
    if not claims:
        print(f"no claims for domain '{domain}'"); return
    rp = os.path.join(tree, f"everything-{domain}", "report.json")
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    kept = bst.cull(claims, min_score=0.50)          # match build (the 0.40 relax was a verified no-op)
    cl = bst.cluster(kept, thresh=0.50)              # match build (0.58 collapsed ★ corroboration)
    rep = bst.subskill_report(domain, cl)
    if old and (rep["multi_source"] < old.get("multi_source", 0)
                or rep["avg_confidence"] < old.get("avg_confidence", 0)):
        print(f"no quality gain (★ {rep['multi_source']} vs {old.get('multi_source')}, "
              f"conf {rep['avg_confidence']} vs {old.get('avg_confidence')}); kept current — NO WRITE")
        return
    name, content = bst.render_subskill(domain, cl, 60, rep)  # more points per section
    bst.write_skill(tree, name, content)
    json.dump(rep, open(os.path.join(tree, name, "report.json"), "w"), indent=2)
    log = os.path.join(tree, "everything", "_adaptation_log.md")
    if os.path.isdir(os.path.dirname(log)):
        open(log, "a").write(f"- {datetime.date.today().isoformat()} improve {name}: "
                             f"{old.get('points')} -> {rep['points']} pts, ★ {rep['multi_source']} "
                             f"(status {rep['status']})\n")
    print(f"improved everything-{domain}: {old.get('points')} -> {rep['points']} pts, "
          f"★ {rep['multi_source']}, status {rep['status']}")


def enrich(domain, claims_dir):
    """List corpus videos relevant to a branch that aren't distilled yet (feed a re-distill)."""
    pat = re.compile(DOMAIN_KW.get(domain, domain), re.I)
    done = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "claims", "*.json"))}
    cands = []
    for f in glob.glob(os.path.join(ROOT, "corpus", "*.json")):
        if f.endswith("corpus.jsonl"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d["id"] in done or not d.get("has_captions"):
            continue
        hay = (d.get("title", "") + " " + d.get("description", "")[:300])
        if pat.search(hay):
            cands.append((d.get("view_count") or 0, d["id"], d.get("title", "")[:55]))
    cands.sort(reverse=True)
    print(f"{len(cands)} undistilled videos relevant to '{domain}':")
    for v, i, t in cands[:30]:
        print(f"  {i}  {v:>10,}  {t}")
    print(f"\n-> distill these (e.g. add to a batch and run distill_workflow) to grow the branch.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--improve", metavar="DOMAIN")
    ap.add_argument("--enrich", metavar="DOMAIN")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--tree", default=bst.GLOBAL_SKILLS)
    ap.add_argument("--claims-dir", default=bst.CLAIMS)
    a = ap.parse_args()
    if a.audit:
        audit(a.tree)
    elif a.improve:
        improve(a.improve, a.tree, a.claims_dir)
    elif a.enrich:
        enrich(a.enrich, a.claims_dir)
    elif a.rebuild:
        os.system(f"python3 {os.path.join(HERE, 'build_skilltree.py')} "
                  f"--claims-dir {a.claims_dir} --install --target {a.tree}")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
