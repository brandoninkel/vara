#!/usr/bin/env python3
"""
Free YouTube ingester for the /everything skill tree.

yt-dlp does it all, no API key / no quota:
  - discovery: channel /videos pages + ytsearch queries
  - transcript: srv1 auto/manual captions (clean, compact) -> json3 -> vtt fallback
  - signal: top comments with like_count (the bullshit meter) + view/like metadata

Output: one corpus/<id>.json per video + an appended corpus.jsonl manifest.
Resume-safe: a video whose corpus/<id>.json exists is skipped.

Usage:
  python3 ingest.py --max-per-channel 30 --concurrency 4 --with-comments --max-comments 40
  python3 ingest.py --only "Andrej Karpathy" --max-per-channel 5            # quick proof
"""
import argparse, concurrent.futures as cf, glob, html, json, os, re, shutil
import subprocess, sys, tempfile, threading, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "corpus")
MANIFEST = os.path.join(CORPUS, "corpus.jsonl")
_LOCK = threading.Lock()
_PRINTLOCK = threading.Lock()
SLEEP_SUBS = "0.4"     # per-subtitle sleep (429-prone call); tunable via --sleep-subs
SLEEP_REQS = "0.2"     # per-request sleep; tunable via --sleep-reqs
COOKIE_ARGS = []       # e.g. ["--cookies-from-browser","safari"] — clears YouTube bot gate


def log(*a):
    with _PRINTLOCK:
        print(*a, flush=True)


def run(cmd, timeout=180):
    """Run yt-dlp, return (rc, stdout, stderr). Never raises on nonzero."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


# ----- transcript parsers -------------------------------------------------
def _unescape(s):
    s = html.unescape(html.unescape(s or ""))  # captions are often double-encoded
    return s


def parse_srv1(text):
    parts = re.findall(r"<text[^>]*>(.*?)</text>", text, re.S)
    parts = [_unescape(re.sub(r"<[^>]+>", " ", p)) for p in parts]
    return clean(" ".join(parts))


def parse_json3(data):
    out = []
    for ev in data.get("events", []):
        for seg in ev.get("segs") or []:
            out.append(seg.get("utf8", ""))
    return clean(_unescape("".join(out)))


def parse_vtt(text):
    lines, prev = [], None
    for ln in text.splitlines():
        ln = ln.strip()
        if (not ln or "-->" in ln or ln.startswith(("WEBVTT", "Kind:", "Language:"))
                or ln.isdigit()):
            continue
        ln = _unescape(re.sub(r"<[^>]+>", "", ln))
        if ln and ln != prev:           # drop rolling-window dups
            lines.append(ln)
            prev = ln
    return clean(" ".join(lines))


def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def en_caption_listed(info):
    """True if info.json advertises any English caption/auto-caption track."""
    for key in ("subtitles", "automatic_captions"):
        for lang in (info.get(key) or {}):
            if lang == "en" or lang.startswith("en"):
                return True
    return False


def extract_comments(info, max_comments):
    cs = []
    for c in (info.get("comments") or [])[:max_comments]:
        cs.append({
            "text": clean(c.get("text", ""))[:500],
            "likes": c.get("like_count") or 0,
            "author": c.get("author"),
            "is_favorited": bool(c.get("is_favorited")),
        })
    cs.sort(key=lambda c: c["likes"], reverse=True)
    return cs


def extract_transcript(tmp, vid):
    """Return (text, source, lang). Prefer srv1 > json3 > vtt; prefer manual > auto."""
    cand = []
    for f in glob.glob(os.path.join(tmp, f"{glob.escape(vid)}*")):
        b = os.path.basename(f)
        m = re.search(rf"{re.escape(vid)}\.([\w-]+)\.(srv1|json3|vtt)$", b)
        if not m:
            continue
        lang, ext = m.group(1), m.group(2)
        cand.append((f, lang, ext))
    if not cand:
        return "", "none", ""
    rank_ext = {"srv1": 0, "json3": 1, "vtt": 2}
    # prefer plain en/manual-ish langs and best ext
    cand.sort(key=lambda c: (rank_ext.get(c[2], 9), 0 if c[1] in ("en", "en-US", "en-GB") else 1))
    f, lang, ext = cand[0]
    try:
        raw = open(f, encoding="utf-8").read()
        if ext == "srv1":
            return parse_srv1(raw), "srv1", lang
        if ext == "json3":
            return parse_json3(json.loads(raw)), "json3", lang
        return parse_vtt(raw), "vtt", lang
    except Exception as e:
        log("  ! parse fail", vid, ext, e)
        return "", "none", lang


# ----- discovery ----------------------------------------------------------
def list_ids(source_url, limit):
    rc, out, err = run([
        "yt-dlp", "--quiet", "--no-warnings", "--flat-playlist",
        "--playlist-end", str(limit), "--print", "%(id)s", *COOKIE_ARGS, source_url
    ], timeout=120)
    ids = [x.strip() for x in out.splitlines() if re.fullmatch(r"[\w-]{11}", x.strip())]
    if not ids and err:
        log("  ! discovery err", source_url.split("/")[-2:], err.strip().splitlines()[-1][:120])
    return ids


# ----- per-video fetch ----------------------------------------------------
def fetch(vid, seed, with_comments, max_comments):
    dest = os.path.join(CORPUS, f"{vid}.json")
    if os.path.exists(dest):
        return "skip"
    tmp = tempfile.mkdtemp(prefix=f"yt_{vid}_")
    try:
        cmd = [
            "yt-dlp", "--quiet", "--no-warnings", "--skip-download", "--no-playlist",
            "--write-info-json", "--write-auto-subs", "--write-subs",
            "--sub-langs", "en-orig,en,en-US,en-GB",   # NOT en.* (that pulls 100+ translated tracks -> 429)
            "--sub-format", "srv1/json3/vtt/best",
            "--retries", "5", "--fragment-retries", "5", "--extractor-retries", "3",
            "--sleep-subtitles", SLEEP_SUBS, "--sleep-requests", SLEEP_REQS, "--socket-timeout", "30",
            "-o", os.path.join(tmp, "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={vid}",
        ]
        if with_comments:
            cmd[1:1] = ["--write-comments", "--extractor-args",
                        f"youtube:comment_sort=top;max_comments={max_comments},all,{max_comments}"]
        cmd += COOKIE_ARGS
        rc, out, err = run(cmd, timeout=300)
        infos = glob.glob(os.path.join(tmp, f"{vid}.info.json"))
        if not infos:
            return f"fail:{(err or 'no info.json').strip().splitlines()[-1][:80] if err else 'no-info'}"
        info = json.load(open(infos[0], encoding="utf-8"))
        text, src, lang = extract_transcript(tmp, vid)
        if not text and en_caption_listed(info):
            # captions exist but fetch failed (429 / transient) -> don't save, retry next run
            return "retry:caption-fetch-failed (will re-pull next run)"
        comments = extract_comments(info, max_comments)
        rec = {
            "id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "title": info.get("title"),
            "channel": info.get("channel") or info.get("uploader"),
            "channel_id": info.get("channel_id"),
            "upload_date": info.get("upload_date"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
            "categories": info.get("categories"),
            "tags": (info.get("tags") or [])[:25],
            "description": (info.get("description") or "")[:1500],
            "seed": seed,
            "transcript": text,
            "transcript_source": src,
            "transcript_words": len(text.split()),
            "transcript_lang": lang,
            "has_captions": bool(text),
            "needs_whisper": not bool(text),
            "top_comments": comments,
            "ingested_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False)
        with _LOCK, open(MANIFEST, "a", encoding="utf-8") as mf:
            mf.write(json.dumps({k: rec[k] for k in (
                "id", "title", "channel", "seed", "upload_date", "view_count",
                "like_count", "transcript_words", "transcript_source",
                "has_captions", "needs_whisper")}, ensure_ascii=False) + "\n")
        tag = "OK " if text else "NOCAP"
        return f"{tag} {rec['transcript_words']}w {src} | {(rec['title'] or '')[:60]}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def augment_comments(vid, seed, max_comments):
    """Pull comments only and merge into an existing corpus/<id>.json (no transcript refetch)."""
    dest = os.path.join(CORPUS, f"{vid}.json")
    if not os.path.exists(dest):
        return "skip"                       # nothing to augment
    try:
        rec = json.load(open(dest, encoding="utf-8"))
    except Exception:
        return "fail:bad-record"
    if rec.get("comments_fetched") or rec.get("top_comments"):
        return "skip"                       # already fetched (flag set even if 0 comments)
    tmp = tempfile.mkdtemp(prefix=f"yc_{vid}_")
    try:
        rc, out, err = run([
            "yt-dlp", "--quiet", "--no-warnings", "--skip-download", "--no-playlist",
            "--write-info-json", "--write-comments",
            "--extractor-args",
            f"youtube:comment_sort=top;max_comments={max_comments},all,{max_comments}",
            "--retries", "5", "--extractor-retries", "3",
            "--sleep-requests", "0.7", "--socket-timeout", "30",
            *COOKIE_ARGS,
            "-o", os.path.join(tmp, "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={vid}",
        ], timeout=300)
        infos = glob.glob(os.path.join(tmp, f"{vid}.info.json"))
        if not infos:
            return f"retry:{(err or 'no-info').strip().splitlines()[-1][:70] if err else 'no-info'}"
        info = json.load(open(infos[0], encoding="utf-8"))
        comments = extract_comments(info, max_comments)
        rec["top_comments"] = comments
        rec["comments_fetched"] = True
        if rec.get("comment_count") is None:
            rec["comment_count"] = info.get("comment_count")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False)
        return f"OK  {len(comments)} comments | {(rec.get('title') or '')[:55]}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ----- driver -------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=os.path.join(HERE, "seeds.json"))
    ap.add_argument("--max-per-channel", type=int, default=30)
    ap.add_argument("--max-per-query", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--with-comments", action="store_true")
    ap.add_argument("--max-comments", type=int, default=60,
                    help="top comments to keep; deep enough to catch substantive mid-tier (not just top jokes)")
    ap.add_argument("--only", default=None, help="substring filter on channel label")
    ap.add_argument("--no-queries", action="store_true")
    ap.add_argument("--throttle", type=float, default=0.0, help="sleep between submits (s)")
    ap.add_argument("--augment-comments", action="store_true",
                    help="2nd pass: add comments to existing records that lack them (no transcript refetch)")
    ap.add_argument("--sleep-subs", type=float, default=0.4, help="per-subtitle sleep (s)")
    ap.add_argument("--sleep-reqs", type=float, default=0.2, help="per-request sleep (s)")
    ap.add_argument("--disco-workers", type=int, default=8, help="parallel discovery threads")
    ap.add_argument("--cookies-from-browser", default=None,
                    help="browser to read YouTube cookies from (e.g. safari, chrome) — clears bot gate")
    ap.add_argument("--cookies", default=None, help="path to a cookies.txt file (alt to --cookies-from-browser)")
    args = ap.parse_args()

    global SLEEP_SUBS, SLEEP_REQS, COOKIE_ARGS
    SLEEP_SUBS, SLEEP_REQS = str(args.sleep_subs), str(args.sleep_reqs)
    if args.cookies_from_browser:
        COOKIE_ARGS = ["--cookies-from-browser", args.cookies_from_browser]
    elif args.cookies:
        COOKIE_ARGS = ["--cookies", args.cookies]
    log(f"cookies: {' '.join(COOKIE_ARGS) if COOKIE_ARGS else 'NONE (bot-gate risk)'}")
    os.makedirs(CORPUS, exist_ok=True)

    tasks = []          # (vid, seed_label)
    if args.augment_comments:
        log("== augment-comments: scanning corpus for records missing comments ==")
        for f in glob.glob(os.path.join(CORPUS, "*.json")):
            if f.endswith("corpus.jsonl"):
                continue
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:
                continue
            if not (d.get("comments_fetched") or d.get("top_comments")):
                tasks.append((d["id"], d.get("seed") or "?"))
        log(f"  {len(tasks)} records need comments")
    else:
        cfg = json.load(open(args.seeds, encoding="utf-8"))
        log("== discovery (parallel) ==")
        # build source list: (label, url, limit)
        sources = []
        for ch in cfg.get("channels", []):
            if args.only and args.only.lower() not in ch["label"].lower():
                continue
            sources.append((ch["label"], ch["url"], args.max_per_channel))
        if not args.only and not args.no_queries:
            for q in cfg.get("queries", []):
                sources.append((f"query:{q}", f"ytsearch{args.max_per_query}:{q}", args.max_per_query))
        seen = set()
        with cf.ThreadPoolExecutor(max_workers=args.disco_workers) as dex:
            res = {dex.submit(list_ids, url, lim): label for label, url, lim in sources}
            for fut in cf.as_completed(res):
                label = res[fut]
                ids = fut.result() or []
                new = [i for i in ids if i not in seen]
                seen.update(new)
                tasks += [(i, label) for i in new]
                log(f"  {label[:34]:<34} {len(ids):>3} found, {len(new):>3} new")

    already = 0 if args.augment_comments else sum(
        1 for v, _ in tasks if os.path.exists(os.path.join(CORPUS, f"{v}.json")))
    log(f"\n== {'augment' if args.augment_comments else 'fetch'} == {len(tasks)} candidates, "
        f"{already} already on disk, conc={args.concurrency}\n")

    t0 = time.time()
    done = ok = nocap = fail = skip = retry = 0
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        worker = augment_comments if args.augment_comments else \
            (lambda v, s: fetch(v, s, args.with_comments, args.max_comments))
        futs = {}
        for v, s in tasks:
            futs[ex.submit(worker, v, s, args.max_comments) if args.augment_comments
                 else ex.submit(worker, v, s)] = (v, s)
            if args.throttle:
                time.sleep(args.throttle)
        for fut in cf.as_completed(futs):
            v, s = futs[fut]
            done += 1
            try:
                r = fut.result()
            except Exception as e:
                r = f"fail:{e}"
            if r == "skip":
                skip += 1
            elif r.startswith("OK"):
                ok += 1
            elif r.startswith("NOCAP"):
                nocap += 1
            elif r.startswith("retry"):
                retry += 1
            else:
                fail += 1
            if not r.startswith("skip"):
                log(f"[{done}/{len(tasks)}] {s[:18]:<18} {r}")
    dt = time.time() - t0
    log(f"\n== done in {dt:.0f}s == ok={ok} nocap={nocap} retry={retry} fail={fail} skip={skip}")
    log(f"corpus: {CORPUS}  manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
