#!/usr/bin/env python3
"""
Turn distilled claims (claims/*.json) into the /everything skill tree.

Pipeline:
  1. load all claims
  2. BULLSHIT-METER CULL: weight by comment_support, drop weak/contradicted
  3. cross-source clustering: merge near-duplicate claims, boost ones many
     independent channels agree on
  4. group by domain -> one sub-skill per domain (everything-<domain>)
  5. emit /everything orchestrator that routes to the sub-skills

Builds into a staging dir by default (review first). --install copies to the
global skills dir. Self-learning: rerun after more ingest/distill to refresh.
"""
import argparse, glob, json, os, re, shutil, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLAIMS = os.path.join(ROOT, "claims")
GLOBAL_SKILLS = os.path.expanduser("~/.claude/skills")

SUPPORT_W = {"corroborated": 1.30, "neutral": 1.0, "none": 1.0, "contradicted": 0.45}
# transcript-only trust model (replaces comment bullshit-meter):
HIGH_TRUST_CH = {"Andrej Karpathy", "Anthropic", "AI Engineer", "DeepLearningAI",
                 "Latent Space", "Cognition", "Google DeepMind", "OpenAI"}
CORPUS_META = {}   # id -> {channel, views, date}


def tier_w(channel):
    return 1.20 if channel in HIGH_TRUST_CH else 1.0


def recency_w(date):
    y = str(date or "")[:4]
    return {"2026": 1.15, "2025": 1.05, "2024": 0.95, "2023": 0.85}.get(y, 0.9 if y else 1.0)


def engagement_w(views):
    v = views or 0
    return 1.15 if v >= 1_000_000 else 1.07 if v >= 100_000 else 1.0 if v >= 10_000 else 0.95


def load_corpus_meta():
    import os as _os
    for f in glob.glob(_os.path.join(ROOT, "corpus", "*.json")):
        if f.endswith("corpus.jsonl"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
            CORPUS_META[d["id"]] = {"channel": d.get("channel"),
                                    "views": d.get("view_count"),
                                    "date": d.get("upload_date")}
        except Exception:
            pass
STOP = set("the a an of to and or is are be in on for with this that it as you your "
           "we they i can will how what why use using used get got make made do does "
           "so just like really very more most also if then than from at by about into "
           "one two it's dont don't can't into our their his her them these those".split())


def norm_words(s):
    return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 2]


def sig(s):
    return set(norm_words(s))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_claims(claims_dir):
    out = []
    for f in glob.glob(os.path.join(claims_dir, "*.json")):
        try:
            arr = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(arr, list):
            out.extend(c for c in arr if isinstance(c, dict) and c.get("claim"))
    return out


def score(c):
    conf = float(c.get("confidence") or 0.5)
    m = CORPUS_META.get(c.get("source_id"), {})
    ch = m.get("channel") or c.get("source_channel")
    return (conf * SUPPORT_W.get(c.get("comment_support"), 1.0)
            * tier_w(ch) * recency_w(m.get("date")) * engagement_w(m.get("views")))


def cull(claims, min_score):
    kept = []
    for c in claims:
        s = score(c)
        if s < min_score:
            continue
        if c.get("comment_support") == "contradicted" and float(c.get("confidence") or 0) < 0.7:
            continue
        c["_score"] = s
        c["_sig"] = sig(c["claim"])
        kept.append(c)
    return kept


def cluster(claims, thresh=0.5):
    """Greedy near-dup merge within a domain via overlap-coefficient vs the cluster's
    representative claim (catches the same idea phrased differently across channels,
    which plain Jaccard misses). Returns list of cluster dicts."""
    claims = sorted(claims, key=lambda c: -c["_score"])
    clusters = []
    for c in claims:
        placed = False
        cs = c["_sig"]
        for cl in clusters:
            rs = cl["sig"]                       # representative's signature (stable)
            inter = len(cs & rs)
            if inter >= 3 and inter / (min(len(cs), len(rs)) or 1) >= thresh:
                cl["members"].append(c)
                cl["sources"].add(c.get("source_channel") or "?")
                placed = True
                break
        if not placed:
            clusters.append({"rep": c, "members": [c], "sig": set(cs),
                             "sources": {c.get("source_channel") or "?"}})
    for cl in clusters:
        n_src = len(cl["sources"])
        cl["trust"] = round(cl["rep"]["_score"] * (1 + 0.12 * (n_src - 1)), 3)
        cl["n_src"] = n_src
    clusters.sort(key=lambda cl: -cl["trust"])
    return clusters


TYPE_SECTIONS = [
    ("mental_model", "Mental models"),
    ("technique", "Techniques"),
    ("workflow", "Workflows"),
    ("tip", "Tips"),
    ("tool", "Tools & settings"),
    ("gotcha", "Gotchas & pitfalls"),
    ("fact", "Key facts"),
]


def subskill_report(domain, clusters):
    name = f"everything-{domain}"
    n = len(clusters)
    confs = [float(cl["rep"].get("confidence") or 0) for cl in clusters]
    avg_conf = round(sum(confs) / n, 2) if n else 0.0
    multi = sum(1 for cl in clusters if cl["n_src"] >= 2)
    multi_pct = round(multi / n, 2) if n else 0.0
    types = sorted({(cl["rep"].get("type") or "fact") for cl in clusters})
    # weak = genuinely actionable gaps for self-adaptation. Cross-source ★ is a BONUS
    # signal (lexical matching under-counts it), NOT a weakness trigger.
    weak = []
    if n < 25:
        weak.append("thin (<25 points) — enrich")
    if avg_conf and avg_conf < 0.62:
        weak.append("low avg confidence")
    missing_core = [h for k, h in TYPE_SECTIONS[:4] if k not in
                    {(cl["rep"].get("type") or "fact") for cl in clusters}]
    if n >= 25 and len(missing_core) >= 3:
        weak.append("narrow type coverage")
    missing = [h for k, h in TYPE_SECTIONS if k not in types]
    return {"skill": name, "domain": domain, "points": n, "avg_confidence": avg_conf,
            "multi_source": multi, "multi_source_pct": multi_pct, "types": types,
            "missing_types": missing, "weak": weak, "status": "weak" if weak else "healthy"}


def render_subskill(domain, clusters, per_section, rep):
    name = f"everything-{domain}"
    lines = [f"---", f"name: {name}",
             f"description: Distilled, comment-vetted knowledge on {domain.replace('-', ' ')} "
             f"from top AI YouTube lectures/channels. Loaded by the /everything orchestrator "
             f"when a request touches {domain.replace('-', ' ')}.",
             f"---", "",
             f"# {domain.replace('-', ' ').title()}", "",
             f"_{len(clusters)} vetted points distilled from the corpus. "
             f"★ = corroborated by multiple independent channels (high trust)._", ""]
    by_type = collections.defaultdict(list)
    for cl in clusters:
        by_type[cl["rep"].get("type") or "fact"].append(cl)
    for t, heading in TYPE_SECTIONS:
        cls = by_type.get(t)
        if not cls:
            continue
        lines.append(f"## {heading}")
        for cl in cls[:per_section]:
            r = cl["rep"]
            star = " ★" if cl["n_src"] >= 2 else ""
            badge = "" if cl["rep"].get("comment_support") != "contradicted" else " ⚠️ disputed"
            comm = " 💬(from comments)" if cl["rep"].get("source_kind") == "comment" else ""
            lines.append(f"- **{r['claim'].rstrip('.')}.**{star}{comm}{badge}")
            if r.get("actionable"):
                lines.append(f"  - *Apply:* {r['actionable']}")
            srcs = sorted(cl["sources"])[:3]
            lines.append(f"  - *Source:* {', '.join(srcs)}"
                         + (f" +{cl['n_src']-3} more" if cl["n_src"] > 3 else ""))
        lines.append("")
    lines += ["## Self-audit (read by the /everything orchestrator)", "",
              f"- points: {rep['points']} · avg_confidence: {rep['avg_confidence']} · "
              f"multi-source: {rep['multi_source']} ({int(rep['multi_source_pct']*100)}%)",
              f"- types covered: {', '.join(rep['types']) or 'none'}",
              f"- status: {'⚠️ WEAK — ' + '; '.join(rep['weak']) if rep['weak'] else '✅ healthy'}",
              f"- machine-readable: `report.json` in this folder", ""]
    return name, "\n".join(lines)


def render_orchestrator(domain_stats, total_claims, total_clusters, n_videos, pipeline_dir):
    today = datetime.date.today().isoformat()
    adapt = os.path.join(pipeline_dir, "adapt.py")
    lines = [
        "---", "name: everything",
        "description: Primary orchestrator of a SELF-IMPROVING AI skill tree distilled from "
        "~1900 top AI YouTube lectures, conference talks and agentic-coding channels (Karpathy, "
        "Anthropic, AI Engineer, DeepMind, Stanford, research + builder creators). Use when the "
        "user asks anything about building with AI, LLMs, agents, agent skills, Claude Code, "
        "prompting, RAG, fine-tuning, evals, harness design, ML foundations, or the AI landscape. "
        "Routes to everything-<domain> sub-skills AND adapts the tree to fix its own weaknesses.",
        "---", "",
        "# /everything — Self-Improving AI Skill Tree", "",
        f"_Built {today} from {n_videos} videos → {total_claims} raw claims → "
        f"{total_clusters} vetted, deduped, trust-ranked points across {len(domain_stats)} branches._", "",
        "## How to use this orchestrator", "",
        "1. Identify which domain(s) the user's question touches (branch list below).",
        "2. Invoke the matching `everything-<domain>` sub-skill(s) via the Skill tool to load "
        "that branch's distilled knowledge.",
        "3. Answer grounded in those points. Prefer ★ (multi-source corroborated) points; "
        "treat ⚠️ disputed points with caution. Cite the source channel for load-bearing claims.",
        "",
        "## ⟳ Self-adaptation protocol — RUN EVERY INVOCATION (hardcoded, non-optional)", "",
        "This tree is self-learning: it MUST get stronger every time it is used. On EVERY "
        "invocation, after answering, you MUST run the adaptation loop:", "",
        f"1. **Audit** — run `python3 {adapt} --audit` to read each branch's health (points, "
        "avg confidence, multi-source %, weak flags) gathered from every `everything-*/report.json`.",
        "2. **Detect weakness** in the branch(es) you just used. A branch is WEAK if any hold: "
        "it had NO point relevant to the task; the best point was low-confidence (<0.6) or "
        "⚠️ disputed; the audit flags the branch `weak`; or you had to answer from your own "
        "knowledge because the branch lacked coverage.",
        f"3. **Improve** — for each weak branch D: run `python3 {adapt} --improve D` to "
        "re-mine and re-rank D from the full claim set (relaxed thresholds, more points, "
        "refreshed report). If the gap is a specific correct fact you just established, also "
        "append it as a new point to `everything-D/SKILL.md` and increment its `report.json`. "
        f"For deeper growth run `python3 {adapt} --enrich D` to distill more corpus videos for D.",
        "4. **Log** — append one line to `_adaptation_log.md` (beside these skills): "
        "what branch, what weakness, what action.",
        "5. **Never skip steps 2–4.** Strengthening the tree is part of answering, not optional.",
        "",
        "## Branches (with live health)", "",
    ]
    for d, st in domain_stats:
        flag = "⚠️ WEAK" if st["report"]["weak"] else "✅"
        lines.append(f"- **everything-{d}** — {st['clusters']} pts, {st['multi']} ★multi-src, "
                     f"conf {st['report']['avg_confidence']} {flag}. {d.replace('-', ' ')}.")
    lines += ["",
              "## Trust model (the bullshit meter, transcript-era)", "",
              "Comments were rate-limited out, so trust = ① cross-source corroboration (same "
              "point from N independent channels → ★), ② channel authority tier (Karpathy/"
              "Anthropic/AI Engineer/DeepMind weighted up), ③ recency (2026 > 2024), ④ "
              "view/like engagement. Disputed/low-trust points are dropped or flagged ⚠️.", "",
              "## Pipeline (for --enrich / full refresh)", "",
              f"Pipeline lives at `{pipeline_dir}`. Full refresh: ingest → distill → "
              f"`build_skilltree.py --install`. Per-branch refresh: `adapt.py --improve <domain>`."]
    return "everything", "\n".join(lines)


DOMAIN_KW = {
    "prompting": r"prompt|context window|system prompt|few.?shot",
    "agents": r"\bagent|agentic|tool use|multi.?agent|orchestrat",
    "agentic-coding": r"claude code|cursor|copilot|vibe cod|coding agent|\bhooks?\b|sub.?agent",
    "rag": r"\brag\b|retrieval|embedding|vector",
    "llm-internals": r"transformer|attention|token|architecture|backprop",
    "finetuning": r"fine.?tun|lora|rlhf|distill|post.?training|\bsft\b",
    "evals": r"\beval|benchmark|rubric|llm.as.a.judge",
    "model-landscape": r"gpt|claude|gemini|llama|model release|frontier",
    "inference-serving": r"inference|serving|vllm|quantiz|latency|throughput|deploy",
    "data-curation": r"dataset|synthetic data|data quality|curation",
    "ml-foundations": r"gradient|neural net|statistics|regression|probability",
    "ai-products": r"product|startup|\buser|business|monetiz",
    "safety-alignment": r"alignment|safety|interpretab|jailbreak|guardrail",
    "automation": r"\bn8n|make\.com|zapier|workflow automation|no.?code",
    "research-frontiers": r"paper|sota|state of the art|novel|research",
    "career-learning": r"learn|career|roadmap|beginner|how to start",
}


def reroute_domain(text, vocab):
    """Rescue a claim whose domain tag isn't a real branch (mis-tagged with a type/etc):
    keyword-match its text to a branch instead of dumping it in research-frontiers."""
    t = (text or "").lower()
    for d, pat in DOMAIN_KW.items():
        if d in vocab and re.search(pat, t):
            return d
    return "research-frontiers"


def write_skill(base, name, content):
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=float, default=0.50)
    ap.add_argument("--per-section", type=int, default=40, help="max points per type section")
    ap.add_argument("--stage", default=os.path.join(ROOT, "skilltree_build"))
    ap.add_argument("--install", action="store_true", help="copy staged tree to --target")
    ap.add_argument("--target", default=GLOBAL_SKILLS,
                    help="install destination (default ~/.claude/skills; use ./.claude/skills for local test)")
    ap.add_argument("--domains", default=os.path.join(HERE, "domains.json"))
    ap.add_argument("--claims-dir", default=CLAIMS, help="dir of claims/*.json from distill")
    args = ap.parse_args()

    vocab = json.load(open(args.domains))["domains"]
    load_corpus_meta()
    claims = load_claims(args.claims_dir)
    if not claims:
        print(f"no claims in {args.claims_dir} (run distill first)"); return
    n_videos = len({c.get("source_id") for c in claims})
    kept = cull(claims, args.min_score)
    by_domain = collections.defaultdict(list)
    rerouted = 0
    for c in kept:
        d = c.get("domain")
        if d not in vocab:
            d2 = reroute_domain(c.get("claim", ""), vocab)
            rerouted += d2 != "research-frontiers"
            d = d2
        by_domain[d].append(c)
    if rerouted:
        print(f"rerouted {rerouted} mis-tagged claims to real branches (were orphaned)")

    if os.path.isdir(args.stage):
        shutil.rmtree(args.stage)
    os.makedirs(args.stage, exist_ok=True)

    domain_stats, total_clusters = [], 0
    for d in vocab:
        cl = cluster(by_domain.get(d, []))
        if not cl:
            continue
        total_clusters += len(cl)
        multi = sum(1 for x in cl if x["n_src"] >= 2)
        rep = subskill_report(d, cl)
        name, content = render_subskill(d, cl, args.per_section, rep)
        write_skill(args.stage, name, content)
        json.dump(rep, open(os.path.join(args.stage, name, "report.json"), "w"), indent=2)
        domain_stats.append((d, {"clusters": len(cl), "multi": multi, "report": rep}))

    name, content = render_orchestrator(domain_stats, len(claims), total_clusters,
                                        n_videos, HERE)
    write_skill(args.stage, name, content)
    # tree-level health + seed adaptation log (orchestrator reads/appends these)
    health = {"built": datetime.date.today().isoformat(), "videos": n_videos,
              "claims": len(claims), "clusters": total_clusters,
              "branches": {d: st["report"] for d, st in domain_stats}}
    json.dump(health, open(os.path.join(args.stage, "everything", "_tree_health.json"), "w"), indent=2)
    open(os.path.join(args.stage, "everything", "_adaptation_log.md"), "w").write(
        f"# /everything adaptation log\n\nBuilt {health['built']}: "
        f"{n_videos} videos, {total_clusters} points, {len(domain_stats)} branches.\n"
        f"Weak at build: {[d for d, st in domain_stats if st['report']['weak']] or 'none'}\n")

    print(f"claims: {len(claims)} raw  ->  {len(kept)} kept  ->  {total_clusters} clusters")
    print(f"videos: {n_videos}  domains with content: {len(domain_stats)}")
    for d, st in domain_stats:
        flag = "  ⚠️WEAK" if st["report"]["weak"] else ""
        print(f"  everything-{d:<18} {st['clusters']:>4} pts  ({st['multi']} multi-source){flag}")
    print(f"staged at: {args.stage}")

    if args.install:
        target = args.target
        os.makedirs(target, exist_ok=True)
        for sk in os.listdir(args.stage):
            src, dst = os.path.join(args.stage, sk), os.path.join(target, sk)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        print(f"INSTALLED {len(domain_stats)+1} skills -> {target}")
    else:
        print("review the staged tree, then rerun with --install to deploy")


if __name__ == "__main__":
    main()
