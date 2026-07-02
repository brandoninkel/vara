#!/usr/bin/env python3
"""
Local test harness for the /everything tree: simulate the orchestrator.
Given a question, route to the most relevant everything-<domain> sub-skill(s)
and surface the best-matching distilled points. Proves the tree is queryable.

  python3 pipeline/ask.py "how do I stop Claude Code deleting my files?"
  python3 pipeline/ask.py --tree ./.claude/skills "best way to eval agents"
"""
import sys, os, re, glob, argparse, collections

STOP = set("the a an of to and or is are be in on for with this that it as you your we "
           "they i can how what why use do does my me at by from".split())


def terms(s):
    return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 2]


def load_points(tree):
    """Return [(domain, point_text, source)] parsed from sub-skill SKILL.md bullets."""
    pts = []
    for d in sorted(glob.glob(os.path.join(tree, "everything-*"))):
        dom = os.path.basename(d).replace("everything-", "")
        sk = os.path.join(d, "SKILL.md")
        if not os.path.exists(sk):
            continue
        cur, src = None, ""
        for line in open(sk, encoding="utf-8"):
            line = line.rstrip()
            m = re.match(r"- \*\*(.+?)\*\*", line)
            if m:
                if cur:
                    pts.append((dom, cur, src))
                cur, src = m.group(1), ""
            elif "*Source:*" in line:
                src = line.split("*Source:*", 1)[1].strip()
            elif "*Apply:*" in line and cur:
                cur += "  → " + line.split("*Apply:*", 1)[1].strip()
        if cur:
            pts.append((dom, cur, src))
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+")
    ap.add_argument("--tree", default="./.claude/skills")
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    q = " ".join(a.query)
    qt = set(terms(q))
    pts = load_points(a.tree)
    if not pts:
        print(f"no points in {a.tree}"); return

    # route: score domains by aggregate term overlap
    dom_score = collections.Counter()
    scored = []
    for dom, txt, src in pts:
        tt = terms(txt + " " + dom)
        s = sum(tt.count(w) for w in qt) + (2 if any(w in dom for w in qt) else 0)
        if s:
            scored.append((s, dom, txt, src))
            dom_score[dom] += s
    scored.sort(key=lambda x: -x[0])

    print(f"Q: {q}\n")
    routed = [d for d, _ in dom_score.most_common(3)]
    print(f"→ /everything routes to: {', '.join('everything-' + d for d in routed) or '(no match)'}\n")
    print(f"Top {a.top} distilled points:")
    for s, dom, txt, src in scored[:a.top]:
        print(f"  [{dom}] {txt[:200]}")
        if src:
            print(f"       ({src})")


if __name__ == "__main__":
    main()
