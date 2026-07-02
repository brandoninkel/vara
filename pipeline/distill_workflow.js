export const meta = {
  name: 'distill-corpus',
  description: 'Haiku fleet distills YouTube AI transcripts into scored, comment-vetted knowledge claims',
  phases: [{ title: 'Distill', detail: 'one Haiku agent per size-bounded batch of videos' }],
}

// args = { corpusDir, claimsDir, domains:[...], and EITHER batches:[...] OR batchesPath:"file" }
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const corpusDir = A.corpusDir
const claimsDir = A.claimsDir
const DOMAINS = (A.domains || []).join(', ')

const batchesPath = A.batchesPath
// WORK ITEMS: inline batches (pilot) OR index-mode where each agent reads its OWN
// slice from batchesPath. Index-mode avoids a single huge bootstrap return (364
// batches) that overwhelms the model and stalls the whole run.
let work = []
if (A.batches && A.batches.length) {
  work = A.batches.map((b, i) => ({ idx: (b.batch != null ? b.batch : i), ids: b.ids, words: b.words || 0, inline: true }))
} else if (batchesPath && A.batchCount) {
  for (let i = 0; i < A.batchCount; i++) work.push({ idx: i, inline: false })
}
log(`distilling ${work.length} batches (${work.length && work[0].inline ? 'inline' : 'index'} mode), corpusDir=${corpusDir ? 'ok' : 'MISSING'}`)

const SUMMARY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['batch', 'videosProcessed', 'claimsWritten', 'topDomains'],
  properties: {
    batch: { type: 'integer' },
    videosProcessed: { type: 'integer' },
    claimsWritten: { type: 'integer' },
    topDomains: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
}

function whichVideos(w) {
  if (w.inline) {
    return `Read EACH of these corpus files (one YouTube video per file):\n` +
      w.ids.map(id => `${corpusDir}/${id}.json`).join('\n')
  }
  return `Read the JSON file at ${batchesPath} (a JSON array). Take ONLY the element at ` +
    `index ${w.idx}; it has an "ids" array of YouTube video ids. For EACH id in that ` +
    `array, read the corpus file at ${corpusDir}/<id>.json (one video per file).`
}

function promptFor(w) {
  return `You are a knowledge-distillation worker building a global AI skill tree.

${whichVideos(w)}

Each file is JSON: { id, title, channel, view_count, like_count, transcript, top_comments:[{text,likes,author}], ... }.

TWO knowledge sources per video — mine BOTH:

A) TRANSCRIPT — extract the REUSABLE, ACTIONABLE knowledge: techniques, tips,
   mental models, workflows, gotchas/pitfalls, concrete tool/setting recommendations,
   well-supported facts. IGNORE intros, sponsor reads, self-promo, filler, pure opinion.

B) COMMENTS — the audience often adds REAL VALUE the video missed: corrections
   ("actually X is wrong, do Y"), better approaches, extra resources/tools, caveats,
   real-world results, version updates. Extract those as claims too (set source_kind:
   "comment"). IGNORE jokes, memes, pure praise, and low-effort reactions — note that
   the HIGHEST-liked comments are often jokes, so judge by SUBSTANCE, not likes alone.
   A substantive comment with modest likes beats a high-liked joke.

Quality over quantity: 3-15 strong claims per video across both sources. Skip a video
entirely if it has no real substance.

Also use comments as a BULLSHIT METER on transcript claims (below).

For each claim assign:
- source_kind: "transcript" | "comment"
- domain: ONE of [${DOMAINS}]
- type: technique | tip | mental_model | workflow | gotcha | tool | fact
- actionable: one sentence on HOW to apply it (imperative)
- comment_support (the BULLSHIT METER): inspect top_comments weighted by likes.
    "corroborated"  = high-liked comments confirm/praise/expand this point
    "contradicted"  = high-liked comments call it wrong, outdated, scammy, or misleading
    "neutral"       = comments discuss it without clear verdict
    "none"          = comments don't touch this claim
- confidence: 0.0-1.0 (raise for specific/reproducible claims from high-trust channels
    with corroboration; lower for vague claims or those comments contradict)

Then WRITE one file per video to: ${claimsDir}/<video_id>.json
Content = a JSON array of claim objects, each EXACTLY:
{ "claim": str, "domain": str, "type": str, "actionable": str,
  "source_kind": "transcript"|"comment", "comment_support": str, "confidence": number,
  "source_id": str, "source_channel": str, "source_title": str }
Write valid JSON only (no markdown fences). If a video yields nothing, write [].

After processing all videos, return the summary (the StructuredOutput tool).`
}

const summaries = await parallel(
  work.map(w => () =>
    agent(promptFor(w), {
      label: `distill:batch${w.idx}${w.inline ? `(${w.ids.length}v)` : ''}`,
      phase: 'Distill',
      model: 'haiku',
      effort: 'low',
      schema: SUMMARY_SCHEMA,
    })
  )
)

const ok = summaries.filter(Boolean)
const totalClaims = ok.reduce((n, s) => n + (s.claimsWritten || 0), 0)
const totalVideos = ok.reduce((n, s) => n + (s.videosProcessed || 0), 0)
const domainCount = {}
for (const s of ok) for (const d of (s.topDomains || [])) domainCount[d] = (domainCount[d] || 0) + 1
log(`distilled ${totalVideos} videos -> ${totalClaims} claims across ${ok.length}/${work.length} batches`)
return { batchesOk: ok.length, batchesTotal: work.length, totalVideos, totalClaims, domainCount }
