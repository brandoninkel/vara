#!/bin/zsh
# Resume-till-full supervisor for the targeted ingest.
# - never loses data: ingest.py is resume-safe (skips videos already on disk)
# - relaunches on death/failure; repeats until no new videos can be captured
# - stops after STALL_MAX consecutive rounds that add 0 new videos
#   (remaining are genuinely uncapturable: no captions / private / removed)
cd "$(dirname "$0")/.." || exit 1
LOG=pipeline/supervise.log
INGEST_ARGS=(--max-per-channel 150 --max-per-query 40 --concurrency 4 \
  --disco-workers 6 --sleep-subs 0.5 --sleep-reqs 0.3 --cookies-from-browser safari)
STALL_MAX=3
ROUND_MAX=40

count(){ find corpus -maxdepth 1 -name '*.json' ! -name 'corpus.jsonl' 2>/dev/null | wc -l | tr -d ' '; }

echo "=== supervisor start $(date '+%H:%M:%S') corpus=$(count) ===" >> $LOG
stall=0
for round in $(seq 1 $ROUND_MAX); do
  before=$(count)
  if pgrep -f 'pipeline/ingest.py' >/dev/null; then
    echo "[r$round $(date '+%H:%M:%S')] ingest already running; waiting" >> $LOG
  else
    echo "[r$round $(date '+%H:%M:%S')] launching resume; corpus=$before" >> $LOG
    python3 pipeline/ingest.py "${INGEST_ARGS[@]}" >> pipeline/ingest_rounds.log 2>&1
  fi
  # wait for whatever ingest is running to finish
  while pgrep -f 'pipeline/ingest.py' >/dev/null; do sleep 15; done
  after=$(count)
  echo "[r$round $(date '+%H:%M:%S')] done; corpus $before -> $after" >> $LOG
  if [ "$after" -le "$before" ]; then stall=$((stall+1)); else stall=0; fi
  if [ "$stall" -ge "$STALL_MAX" ]; then
    echo "=== FULL CAPTURE: $stall stalled rounds, remaining uncapturable. corpus=$after ===" >> $LOG
    break
  fi
  sleep 5
done
echo "=== SUPERVISOR DONE $(date '+%H:%M:%S') corpus=$(count) ===" >> $LOG
