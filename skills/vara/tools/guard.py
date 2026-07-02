#!/usr/bin/env python3
"""
Portable safety net for /vara self-evolution. Lives INSIDE the skill folder so it
travels with it — zero external dependencies beyond Python 3 stdlib.

  guard.py --snapshot                  # back up ~/.claude/skills + metrics; prints SNAPDIR
  guard.py --verify --against SNAPDIR  # re-measure; auto-restore snapshot if regressed
  guard.py --lock | --unlock           # concurrency lock for self-edits (fails if held)

Regression = a core skill (vara/vishnu/concert/everything) disappears or fails validation,
total tree points/★ drop >3%, or any branch is gutted >40%. Cross-branch movement is fine.
"""
import argparse, datetime, glob, json, os, re, shutil, sys

HOME = os.path.expanduser("~")
SKILLS = os.path.join(HOME, ".claude", "skills")
BACKUPS = os.path.join(HOME, ".claude", "skills_backups")
LOCK = os.path.join(SKILLS, "vara", "_evolving.lock")
CORE = ("vara", "vishnu", "concert", "everything")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TOL = 0.97


def validate_skill(d):
    """Minimal inline validation: frontmatter, kebab name matching dir, nonempty description."""
    sk = os.path.join(d, "SKILL.md")
    if not os.path.exists(sk):
        return f"{os.path.basename(d)}: missing SKILL.md"
    txt = open(sk, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m:
        return f"{os.path.basename(d)}: no frontmatter"
    nm = re.search(r"^name:\s*(\S+)", m.group(1), re.M)
    if not nm or nm.group(1) != os.path.basename(d) or not NAME_RE.match(nm.group(1)):
        return f"{os.path.basename(d)}: bad/mismatched name"
    if "description:" not in m.group(1):
        return f"{os.path.basename(d)}: no description"
    return None


def metrics():
    m = {"branches": {}, "validate_errors": []}
    for d in sorted(glob.glob(os.path.join(SKILLS, "*"))):
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md")):
            err = validate_skill(d)
            if err:
                m["validate_errors"].append(err)
    for rp in glob.glob(os.path.join(SKILLS, "everything-*", "report.json")):
        try:
            r = json.load(open(rp))
            m["branches"][r["domain"]] = {"points": r["points"], "multi_source": r["multi_source"]}
        except Exception:
            pass
    m["total_points"] = sum(b["points"] for b in m["branches"].values())
    m["total_multi"] = sum(b["multi_source"] for b in m["branches"].values())
    for k in CORE:
        m[f"has_{k}"] = os.path.exists(os.path.join(SKILLS, k, "SKILL.md"))
    m["validate_ok"] = not m["validate_errors"]
    return m


def snapshot():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = os.path.join(BACKUPS, ts)
    os.makedirs(d, exist_ok=True)
    shutil.copytree(SKILLS, os.path.join(d, "skills"),
                    ignore=shutil.ignore_patterns("_evolving.lock"))
    json.dump(metrics(), open(os.path.join(d, "metrics.json"), "w"), indent=2)
    print(d)


def verify(against):
    old = json.load(open(os.path.join(against, "metrics.json")))
    new = metrics()
    reasons = list(new["validate_errors"])
    for k in CORE:
        if old.get(f"has_{k}") and not new.get(f"has_{k}"):
            reasons.append(f"{k} skill disappeared")
    if old.get("total_points") and new["total_points"] < old["total_points"] * TOL:
        reasons.append(f"total points {old['total_points']}->{new['total_points']}")
    if old.get("total_multi") and new["total_multi"] < old["total_multi"] * TOL:
        reasons.append(f"total ★ {old['total_multi']}->{new['total_multi']}")
    for dom, ob in old.get("branches", {}).items():
        nb = new["branches"].get(dom)
        if nb is None:
            reasons.append(f"{dom} branch vanished")
        elif nb["points"] < ob["points"] * 0.6:
            reasons.append(f"{dom} gutted {ob['points']}->{nb['points']}")
    if reasons:
        shutil.rmtree(SKILLS)
        shutil.copytree(os.path.join(against, "skills"), SKILLS)
        print("ROLLBACK — snapshot restored. regressions:")
        for r in reasons:
            print("  -", r)
        sys.exit(2)
    print(f"KEEP — no regression. points {old.get('total_points')}->{new['total_points']}, "
          f"★ {old.get('total_multi')}->{new['total_multi']}, validate ok.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--against")
    ap.add_argument("--lock", action="store_true")
    ap.add_argument("--unlock", action="store_true")
    a = ap.parse_args()
    if a.lock:
        if os.path.exists(LOCK):
            print(f"LOCKED by another session since {open(LOCK).read().strip()} — do NOT self-edit now")
            sys.exit(3)
        open(LOCK, "w").write(datetime.datetime.now().isoformat())
        print("lock acquired")
    elif a.unlock:
        os.path.exists(LOCK) and os.remove(LOCK)
        print("lock released")
    elif a.snapshot:
        snapshot()
    elif a.verify and a.against:
        verify(a.against)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
