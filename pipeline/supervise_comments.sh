#!/bin/zsh
# Resume-till-full supervisor for the COMMENTS augment pass.
# Backfills top comments into every transcript record. Resume-safe: a record with
# comments_fetched=true is skipped. Repeats on death/failure until none remain
# (or STALL_MAX rounds add nothing = remaining have comments disabled / are private).
cd "$(dirname "$0")/.." || exit 1
LOG=pipeline/supervise_comments.log
ARGS=(--augment-comments --concurrency 3 --cookies-from-browser safari --max-comments 60)
STALL_MAX=3
ROUND_MAX=30

remaining(){ python3 -c "
import json,glob
n=0
for f in glob.glob('corpus/*.json'):
    if f.endswith('corpus.jsonl'): continue
    try: d=json.load(open(f))
    except: continue
    if not (d.get('comments_fetched') or d.get('top_comments')): n+=1
print(n)"; }

echo "=== comments supervisor start $(date '+%H:%M:%S') remaining=$(remaining) ===" >> $LOG
stall=0
for round in $(seq 1 $ROUND_MAX); do
  before=$(remaining)
  if pgrep -f 'pipeline/ingest.py' >/dev/null; then
    echo "[r$round $(date '+%H:%M:%S')] ingest already running; waiting" >> $LOG
  else
    echo "[r$round $(date '+%H:%M:%S')] augment round; remaining=$before" >> $LOG
    python3 pipeline/ingest.py "${ARGS[@]}" >> pipeline/comments_rounds.log 2>&1
  fi
  while pgrep -f 'pipeline/ingest.py' >/dev/null; do sleep 15; done
  after=$(remaining)
  echo "[r$round $(date '+%H:%M:%S')] done; remaining $before -> $after" >> $LOG
  if [ "$after" -le 0 ]; then echo "=== ALL COMMENTS FETCHED. ===" >> $LOG; break; fi
  if [ "$after" -ge "$before" ]; then stall=$((stall+1)); else stall=0; fi
  if [ "$stall" -ge "$STALL_MAX" ]; then
    echo "=== COMMENTS FULL: $stall stalled rounds; $after remaining have comments disabled/private ===" >> $LOG
    break
  fi
  sleep 5
done
echo "=== COMMENTS SUPERVISOR DONE $(date '+%H:%M:%S') remaining=$(remaining) ===" >> $LOG
