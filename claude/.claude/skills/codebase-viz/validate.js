#!/usr/bin/env node
/*
 * Validator for codebase-viz output HTML.
 * Usage: node validate.js <path-to-output.html>
 *
 * Checks:
 *   - file exists and has exactly one <script> block
 *   - the embedded JS parses (syntax)
 *   - data-model markers (BEGIN/END) are present and engine is intact
 *   - no {{placeholders}} remain
 *   - ZONES / NODES / KINDS / SCENARIOS are defined and well-formed
 *   - every scenario step's node + edge endpoints resolve to a defined NODE
 *   - every step's `kind` exists in KINDS
 *   - the first SCENARIOS key (shown on load) exists
 * Exit code 0 = OK, 1 = problems found.
 */
const fs = require("fs");

const path = process.argv[2];
if (!path) {
  console.error("usage: node validate.js <path-to-output.html>");
  process.exit(1);
}

const errors = [];
const warnings = [];
const ok = (m) => console.log("  \x1b[32m✓\x1b[0m " + m);

let html;
try {
  html = fs.readFileSync(path, "utf8");
} catch (e) {
  console.error("cannot read " + path + ": " + e.message);
  process.exit(1);
}

// --- structural checks -------------------------------------------------------
const scripts = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
if (scripts.length !== 1) {
  errors.push(`expected exactly 1 <script> block, found ${scripts.length}`);
}
const js = scripts.length ? scripts[0].replace(/<\/?script>/g, "") : "";

if (!html.includes(">>> BEGIN CODEBASE DATA MODEL")) {
  errors.push("missing BEGIN data-model marker");
}
if (!html.includes(">>> END CODEBASE DATA MODEL")) {
  errors.push("missing END data-model marker");
}
for (const fn of ["function renderZones", "function renderNodes", "function animatePacket", "function selectScenario"]) {
  if (!js.includes(fn)) errors.push(`engine appears damaged — '${fn}' not found`);
}

const leftover = html.match(/{{[A-Z_]+}}/g);
if (leftover) errors.push("unfilled placeholders remain: " + [...new Set(leftover)].join(", "));

// --- parse + extract the four consts ----------------------------------------
let ZONES, NODES, KINDS, SCENARIOS;
if (js && js.includes("/* >>> END CODEBASE DATA MODEL <<< */")) {
  try {
    // Evaluate ONLY up to the END marker — that's the data model, which is pure
    // data. The engine below it touches the DOM and would throw under node.
    const modelOnly =
      js.split("/* >>> END CODEBASE DATA MODEL <<< */")[0] +
      ";return { ZONES, NODES, KINDS, SCENARIOS };";
    ({ ZONES, NODES, KINDS, SCENARIOS } = new Function(modelOnly)());
    ok("embedded JS data model parses");
  } catch (e) {
    errors.push("data model eval failed: " + e.message);
  }
} else if (js) {
  // No marker to slice on — just confirm the whole script is syntactically valid.
  try { new Function(js); } catch (e) { errors.push("JS syntax error: " + e.message); }
}

// --- semantic checks ---------------------------------------------------------
if (NODES && typeof NODES === "object") {
  ok(`NODES defined (${Object.keys(NODES).length})`);
} else if (!errors.length) {
  errors.push("NODES is not defined or not an object");
}
if (ZONES && Array.isArray(ZONES)) ok(`ZONES defined (${ZONES.length})`);
else if (!errors.length) errors.push("ZONES is not defined or not an array");

if (KINDS && typeof KINDS === "object") ok(`KINDS defined (${Object.keys(KINDS).length})`);
else if (!errors.length) errors.push("KINDS is not defined or not an object");

if (SCENARIOS && typeof SCENARIOS === "object") {
  const keys = Object.keys(SCENARIOS);
  ok(`SCENARIOS defined (${keys.length}: ${keys.join(", ")})`);

  const nodeKeys = NODES ? new Set(Object.keys(NODES)) : new Set();
  const kindKeys = KINDS ? new Set(Object.keys(KINDS)) : new Set();
  let stepCount = 0;

  for (const sk of keys) {
    const scn = SCENARIOS[sk];
    if (!scn.name) warnings.push(`scenario '${sk}' has no name`);
    if (!Array.isArray(scn.steps) || !scn.steps.length) {
      errors.push(`scenario '${sk}' has no steps`);
      continue;
    }
    scn.steps.forEach((step, i) => {
      stepCount++;
      const loc = `scenario '${sk}' step ${i + 1}`;
      if (step.node && !nodeKeys.has(step.node))
        errors.push(`${loc}: node '${step.node}' is not in NODES`);
      if (step.edge) {
        if (!Array.isArray(step.edge) || step.edge.length !== 2)
          errors.push(`${loc}: edge must be [from, to]`);
        else
          step.edge.forEach((n) => {
            if (!nodeKeys.has(n)) errors.push(`${loc}: edge endpoint '${n}' is not in NODES`);
          });
      }
      if (!step.node && !step.edge)
        errors.push(`${loc}: step has neither node nor edge (nothing to animate)`);
      if (step.kind && !kindKeys.has(step.kind))
        errors.push(`${loc}: kind '${step.kind}' is not in KINDS`);
      if (!step.title) warnings.push(`${loc}: missing title`);
      if (!step.ref) warnings.push(`${loc}: missing source ref (file:line citation)`);
    });
  }
  ok(`${stepCount} total steps checked`);

  // node-in-zone sanity (warn only)
  if (ZONES && NODES) {
    for (const [nk, n] of Object.entries(NODES)) {
      const inSomeZone = ZONES.some(
        (z) => n.x >= z.x - 2 && n.y >= z.y - 2 &&
               n.x + n.w <= z.x + z.w + 2 && n.y + n.h <= z.y + z.h + 2
      );
      if (!inSomeZone) warnings.push(`node '${nk}' is not fully inside any zone box`);
    }
  }
} else if (!errors.length) {
  errors.push("SCENARIOS is not defined or not an object");
}

// --- report ------------------------------------------------------------------
console.log("");
if (warnings.length) {
  console.log("\x1b[33mWarnings:\x1b[0m");
  warnings.forEach((w) => console.log("  ⚠ " + w));
  console.log("");
}
if (errors.length) {
  console.log("\x1b[31mErrors:\x1b[0m");
  errors.forEach((e) => console.log("  ✗ " + e));
  console.log(`\n\x1b[31mFAILED — ${errors.length} error(s).\x1b[0m`);
  process.exit(1);
}
console.log(`\x1b[32mOK — validation passed${warnings.length ? ` (${warnings.length} warning(s))` : ""}.\x1b[0m`);
process.exit(0);
