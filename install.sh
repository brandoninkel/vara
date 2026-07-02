#!/bin/sh
# vara skill-family installer — copies skills into ~/.claude/skills (per-user, any machine).
# Usage:  ./install.sh            # core: /vara /vishnu /concert
#         ./install.sh --with-everything   # + the /everything knowledge tree (17 skills)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"

for s in vara vishnu concert; do
  rm -rf "$DEST/$s"
  cp -r "$HERE/skills/$s" "$DEST/$s"
  echo "installed /$s"
done

if [ "$1" = "--with-everything" ]; then
  for d in "$HERE"/everything-tree/*/; do
    name=$(basename "$d")
    rm -rf "$DEST/$name"
    cp -r "$d" "$DEST/$name"
  done
  echo "installed /everything knowledge tree ($(ls -d "$HERE"/everything-tree/*/ | wc -l | tr -d ' ') skills)"
fi

echo ""
echo "Done. Skills load at the START of a Claude Code session — open a new session and try:"
echo "  /vara <your hardest mission>"
echo "Notes: /vara needs the Workflow tool (subagent orchestration). Self-evolution uses the"
echo "bundled guard at ~/.claude/skills/vara/tools/guard.py (python3, stdlib only)."
