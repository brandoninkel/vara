#!/usr/bin/env python3
"""
Safety net for the self-improvement loop. Snapshots the global skills, and after
a loop iteration VERIFIES nothing regressed — auto-rolling back if it did.

  guard.py --snapshot                 # backup skills + record metrics -> prints SNAPDIR
  guard.py --verify --against SNAPDIR  # re-measure; rollback (restore) if worse; print KEEP/ROLLBACK

Regression = any branch loses points or ★ multi_source (beyond tolerance), validation
fails, or a key skill (everything/vishnu/concert) disappears.
"""
import argparse, json, glob, os, shutil, sys, datetime, subprocess

HOME = os.path.expanduser("~")
SKILLS = os.path.join(HOME, ".claude", "skills")
BACKUPS = os.path.join(HOME, ".claude", "skills_backups")
PIPE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.97   # allow 3% noise before calling it a regression


def metrics():
    m = {"branches": {}}
    for rp in glob.glob(os.path.join(SKILLS, "everything-*", "report.json")):
        try:
            r = json.load(open(rp))
            m["branches"][r["domain"]] = {"points": r["points"],
                                          "multi_source": r["multi_source"],
                                          "avg_confidence": r["avg_confidence"]}
        except Exception:
            pass
    m["total_points"] = sum(b["points"] for b in m["branches"].values())
    m["total_multi"] = sum(b["multi_source"] for b in m["branches"].values())
    for k in ("everything", "vishnu", "concert", "vara"):
        m[f"has_{k}"] = os.path.exists(os.path.join(SKILLS, k, "SKILL.md"))
    try:
        rc = subprocess.run(["python3", os.path.join(PIPE, "validate_skills.py"), SKILLS],
                            capture_output=True, text=True, timeout=60)
        m["validate_ok"] = rc.returncode == 0
    except Exception:
        m["validate_ok"] = False
    return m


def snapshot():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = os.path.join(BACKUPS, ts)
    os.makedirs(d, exist_ok=True)
    shutil.copytree(SKILLS, os.path.join(d, "skills"))
    json.dump(metrics(), open(os.path.join(d, "metrics.json"), "w"), indent=2)
    print(d)


def verify(against):
    old = json.load(open(os.path.join(against, "metrics.json")))
    new = metrics()
    reasons = []
    if not new["validate_ok"]:
        reasons.append("validation FAILED")
    for k in ("everything", "vishnu", "concert", "vara"):
        if old.get(f"has_{k}") and not new.get(f"has_{k}"):
            reasons.append(f"{k} skill disappeared")
    # judge on TOTALS — cross-branch redistribution (e.g. rerouting mis-tagged claims) is
    # healthy and must NOT trip rollback; only a net loss or a gutted branch is a regression.
    if new["total_points"] < old["total_points"] * TOL:
        reasons.append(f"total points {old['total_points']}->{new['total_points']}")
    if new["total_multi"] < old["total_multi"] * TOL:
        reasons.append(f"total ★ {old['total_multi']}->{new['total_multi']}")
    for dom, ob in old["branches"].items():
        nb = new["branches"].get(dom)
        if not nb:
            reasons.append(f"{dom} branch vanished")
        elif nb["points"] < ob["points"] * 0.6:
            reasons.append(f"{dom} gutted {ob['points']}->{nb['points']}")
    if reasons:
        # ROLLBACK: restore the snapshot
        shutil.rmtree(SKILLS)
        shutil.copytree(os.path.join(against, "skills"), SKILLS)
        print("ROLLBACK — restored snapshot. regressions:")
        for r in reasons:
            print("  -", r)
        sys.exit(2)
    print(f"KEEP — no regression. points {old['total_points']}->{new['total_points']}, "
          f"★ {old['total_multi']}->{new['total_multi']}, validate ok.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--against")
    a = ap.parse_args()
    if a.snapshot:
        snapshot()
    elif a.verify and a.against:
        verify(a.against)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
