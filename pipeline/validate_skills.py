#!/usr/bin/env python3
"""Validate a built skill tree: frontmatter, naming rules, sizes, orchestrator wiring."""
import sys, os, re, glob

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def parse_front(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m:
        return None, None, txt
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.group(2), txt


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/skills")
    skills = sorted(d for d in glob.glob(os.path.join(base, "everything*"))
                    if os.path.isdir(d))
    if not skills:
        print(f"no everything* skills in {base}"); return
    errors, warns = [], []
    names = set()
    sub_names = set()
    for d in skills:
        name_dir = os.path.basename(d)
        sk = os.path.join(d, "SKILL.md")
        if not os.path.exists(sk):
            errors.append(f"{name_dir}: missing SKILL.md"); continue
        fm, body, txt = parse_front(sk)
        if fm is None:
            errors.append(f"{name_dir}: no YAML frontmatter"); continue
        nm = fm.get("name", "")
        desc = fm.get("description", "")
        if nm != name_dir:
            errors.append(f"{name_dir}: name '{nm}' != dir")
        if not NAME_RE.match(nm):
            errors.append(f"{name_dir}: name not kebab-case")
        if len(nm) > 64:
            errors.append(f"{name_dir}: name >64 chars")
        if not desc:
            errors.append(f"{name_dir}: empty description")
        if len(desc) > 1024:
            warns.append(f"{name_dir}: description {len(desc)} chars (>1024)")
        wc = len(body.split()) if body else 0
        if wc < 20:
            warns.append(f"{name_dir}: thin body ({wc} words)")
        names.add(nm)
        if nm != "everything":
            sub_names.add(nm)

    # orchestrator wiring
    orch = os.path.join(base, "everything", "SKILL.md")
    if os.path.exists(orch):
        otxt = open(orch, encoding="utf-8").read()
        missing = [s for s in sub_names if s not in otxt]
        if missing:
            warns.append(f"orchestrator doesn't reference: {', '.join(sorted(missing)[:8])}"
                         + (" ..." if len(missing) > 8 else ""))
    else:
        errors.append("no everything orchestrator skill")

    print(f"== validate {base} ==")
    print(f"skills: {len(skills)}  (1 orchestrator + {len(sub_names)} sub-skills)")
    print(f"errors: {len(errors)}  warnings: {len(warns)}")
    for e in errors:
        print(f"  ERROR  {e}")
    for w in warns:
        print(f"  warn   {w}")
    print("OK ✅" if not errors else "FAILED ❌")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
