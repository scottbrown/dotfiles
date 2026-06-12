Analyze the current codebase and generate a self-contained, animated static HTML
page that visualizes how data flows through it — its components, trust
boundaries, external systems, and the key request/data scenarios.

Use the `codebase-viz` skill, which bundles the proven animation engine as a
template, a data-model authoring contract, and a validator. Follow its procedure:

1. **Understand deeply first.** Read entry points and architecture docs, then fan
   out parallel `Explore` subagents (primary data lifecycle · secondary/background
   paths · external systems & trust boundaries) and have each return
   `file:line`-cited findings. Do not animate anything you cannot cite.
2. **Author the data model** (`ZONES`, `NODES`, `KINDS`, `SCENARIOS`) between the
   markers in a copy of the skill's `template.html`. Include the primary happy
   path plus 2–5 scenarios that reveal the architecture's character (a blocked/
   rejected path, a redaction path, an idempotency/write-once path, an admin/read
   path, an auth handshake — whatever fits). Flag every trust-boundary crossing.
3. **Verify** with the skill's `validate.js`, fix anything it flags, then open the
   file and spot-check a couple of the source citations.

Default output path: `docs/architecture-visualization.html` in the current repo
(create `docs/` if needed). If the user passed an argument, treat it as the
desired output path or a focus hint. When done, report the path and offer to open
it.

$ARGUMENTS
