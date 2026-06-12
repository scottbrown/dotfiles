---
name: codebase-viz
description: >
  Generate a self-contained, animated static HTML page that visualizes how data
  flows through any codebase — its components, trust boundaries, external systems,
  and key request/data scenarios. The output is a single dependency-free .html file
  with a stepper, auto-play, and source citations. Use when asked to visualize,
  diagram, or animate a codebase's architecture or data flow.
when_to_use: >
  Visualize codebase architecture, animate data flow, architecture diagram, trust
  boundary diagram, data-flow visualization, "show me how this codebase works"
  visually, onboarding diagram, request lifecycle animation, single-file HTML
  architecture page.
allowed-tools: Read Grep Glob Bash Agent Write Edit
user-invocable: true
---

# Codebase Data-Flow Visualization

This skill produces a **single, self-contained, animated HTML file** that walks a
viewer through how data flows across a codebase: from untrusted input, across
trust boundaries, through internal components, out to external systems, and back.
It is dependency-free (pure SVG + vanilla JS), runs by double-clicking, and cites
real `file:line` references on every step.

## How it works

The HTML file is split into two parts:

1. **A generic animation engine** — CSS, SVG rendering, the step/play state
   machine, packet animation, legend, scenario buttons. This is identical for
   every codebase and **must never be edited**.
2. **A codebase-specific data model** — four JavaScript consts (`ZONES`,
   `NODES`, `KINDS`, `SCENARIOS`) that describe *this* codebase. This is the
   **only** thing you author.

The engine lives in `template.html` (next to this file). The data model sits
between two markers:

```
/* >>> BEGIN CODEBASE DATA MODEL ... <<< */
   ...the four consts...
/* >>> END CODEBASE DATA MODEL <<< */
```

Your job: **analyze the target codebase, then replace everything between those
two markers** (and fill three `{{...}}` placeholders in the header). Do not touch
anything outside the markers.

## Procedure

### Step 1 — Understand the codebase (deeply)

This is the part that makes the output good. Do not skim. Budget real effort here.

1. Read the entry points (README, `main`/`cmd`, `index`, route definitions,
   handlers, framework bootstrap) and any architecture docs (`CLAUDE.md`,
   `ARCHITECTURE.md`, `docs/`).
2. For a non-trivial codebase, **fan out parallel `Explore` (or `general-purpose`)
   subagents** — one per concern — and have each return file:line-cited findings.
   Good splits:
   - **Primary request/data lifecycle**: entry → validation → core logic →
     response. The main path a unit of data takes.
   - **Secondary paths & background jobs**: auth, webhooks, queues, cron,
     admin/back-office, batch.
   - **External systems & trust boundaries**: every DB, cache, queue, third-party
     API, LLM, object store, payment processor; where untrusted input enters;
     where identity/PII is transformed; where the system fails open vs closed.
3. While reading, capture for **every hop**: the source file:line, what data
   moves, and whether the hop crosses a trust boundary (untrusted→trusted,
   internal→external, raw-identity→hashed, plaintext→validated, etc.).

You cannot animate what you don't understand. The citations must be real — verify
them with `grep`/`Read` before writing them. Never invent a `file:line`.

### Step 2 — Design the layout

- **Zones** = trust/ownership regions, laid out left→right in data-flow order.
  Typical zones: `Untrusted` (clients) · `Edge` (LB/gateway/CDN) · the app
  itself (often the widest) · external/managed services · data &
  observability. Use 3–6 zones. Pick whatever the codebase actually has.
- **Nodes** = components, placed *inside* the zone they belong to. Aim for
  12–28 nodes — enough to be faithful, few enough to read.
- **Scenarios** = the stories worth animating. Always include the primary happy
  path. Then add the ones that reveal the architecture's *character*: a rejected/
  blocked path, a redaction/masking path, a write-once or idempotency path, an
  admin/read path, an auth handshake, a cache hit/miss, a retry/failure. 3–6
  scenarios is the sweet spot.

### Step 3 — Author the data model

Replace the block between the markers. The exact shapes:

```js
const ZONES = [
  // x,y = top-left; w,h = size. Lay zones out across an 1480 x 840 viewBox.
  { x:20, y:70, w:200, h:700,
    fill:'var(--z-untrusted)', stroke:'#f8514955',
    label:'Untrusted', sub:'clients' },
  // ...3–6 zones, left to right
];

const NODES = {
  // key is referenced by scenario steps. Place each node inside its zone's box.
  // x,y = top-left; w ~150–210, h ~48–58. sub renders in monospace (good for
  // env vars, endpoints, file hints).
  n_handler: { x:300, y:200, w:160, h:56, label:'Handler', sub:'POST /things' },
  // ...
};

const KINDS = {
  // Flow types -> color + legend label. Keep the keys below; only relabel them
  // to fit the domain (e.g. for a non-LLM app, repurpose 'llm'->'compute' by
  // changing the label string). Each key maps to a CSS var already defined.
  data:      { color:'var(--k-data)',      label:'Trusted data' },
  untrusted: { color:'var(--k-untrusted)', label:'Untrusted input' },
  llm:       { color:'var(--k-llm)',       label:'LLM inference' },
  guard:     { color:'var(--k-guard)',     label:'Validation' },
  block:     { color:'var(--k-block)',     label:'Rejected' },
  mask:      { color:'var(--k-mask)',      label:'Redacted' },
  store:     { color:'var(--k-store)',     label:'Persist' },
  tool:      { color:'var(--k-tool)',      label:'External call' },
  internal:  { color:'var(--k-internal)',  label:'Internal' },
};

const SCENARIOS = {
  // first key is shown on load
  happy: {
    name: 'Request — happy path',          // button label
    blurb: 'One-sentence summary shown before stepping.',
    steps: [
      {
        edge: ['n_client','n_handler'],     // [from, to] node keys; omit on a
                                            // step that just highlights a node
        node: 'n_handler',                  // node to spotlight (defaults to edge[1])
        kind: 'untrusted',                  // a key from KINDS -> color
        title: 'Request enters at the edge',
        hop:   'client ──▶ handler',        // short monospace route line
        detail:'1–3 sentences. What happens, and the security-relevant nuance ' +
               '(fail-open vs closed, what is validated, what is trusted).',
        ref:   'src/http/handler.go:42',    // REAL file:line — verified
        boundary: { text:'Trust boundary: untrusted input enters.' }
        // boundary is optional. Add { safe:true, text:'...' } for a *protective*
        // boundary (e.g. identity hashed, PII redacted) — renders green.
      },
      // ...more steps in order
    ],
  },
  // ...more scenarios
};
```

**Authoring rules**

- Every `edge`'s two endpoints and every `node` must be keys that exist in
  `NODES`. The engine dims out-of-scenario nodes automatically.
- Use `kind:'block'`/`'mask'` on the step where a rejection/redaction actually
  happens — those tint the node red/orange, which reads instantly.
- Use `boundary` on steps that cross a trust line. Plain `{text}` = a risk
  crossing (red ⚠); `{safe:true,text}` = a protective transform (green 🔒).
- `detail` should teach, not narrate. Prefer "fails closed — an error replaces
  the answer" over "calls the function".
- Keep `ref` real and specific. If you can't cite it, you don't understand it
  well enough to animate it — go read more.

### Step 4 — Assemble the file

1. Copy `template.html` from this skill's directory to the output path (default:
   `docs/architecture-visualization.html` in the target repo; create `docs/` if
   absent, or ask where to put it).
2. Replace the three header placeholders:
   - `{{PROJECT_NAME}}` (appears twice) → the project name.
   - `{{PROJECT_TAGLINE}}` → a short subtitle, e.g.
     `Animated trust-boundary walkthrough · generated from source`.
3. Replace everything **between** the `BEGIN`/`END` markers with your authored
   `ZONES`, `NODES`, `KINDS`, `SCENARIOS`. Leave the markers themselves and
   everything outside them untouched.

### Step 5 — Verify before claiming done

Run the validator script bundled with this skill:

```bash
node "$HOME/.claude/skills/codebase-viz/validate.js" <path-to-output.html>
```

It checks: the embedded JS parses; every `edge`/`node` reference resolves to a
defined node; every `kind` exists in `KINDS`; no `{{placeholders}}` remain; the
engine markers are intact. Fix anything it flags. Then open the file
(`open <path>` on macOS) and confirm it renders and steps through.

Spot-check 2–3 of your `ref` citations with `grep`/`Read` to confirm they point
at the right lines.

## Layout cheatsheet

- viewBox is `1480 x 840`. Keep nodes within their zone's rectangle.
- Zones span `y:70` to `y:790` typically; give each a comfortable width.
- Nodes: `w` 150–210, `h` 48–58. Stack them vertically ~70px apart inside a zone.
- Curved edges auto-separate overlapping routes, so two nodes can have edges in
  both directions without overlap.
- `sub` text is monospaced — ideal for endpoints, env var names, or a file hint.

## Output

A single `.html` file. No build step, no network, no dependencies. The user opens
it in any browser: scenario buttons (top-right), Play/Pause, Prev/Next, a speed
slider, keyboard arrows + space, a progress strip, and a per-step narration panel
with the source citation. Tell the user the path and offer to open it.
