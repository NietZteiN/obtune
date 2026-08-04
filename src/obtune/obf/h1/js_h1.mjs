// QUARANTINED JavaScript H1 generator — string encoding via javascript-obfuscator.
//
// HARD RULE (CLAUDE.md §3.2): this file lives under obf/h1/ and is invoked ONLY
// by scripts/gen_h1_quarantined.py. javascript-obfuscator is confined here because
// its rc4 stringArray is exactly the held-out H1 feature; letting it touch any
// trainable condition would leak the discriminator (tests/test_quarantine_lint.py
// asserts no other .mjs references it).
//
// H1 mirrors the Python side conceptually: string ENCODING is the primary held-out
// feature (rc4 string array + splitStrings), with numbersToExpressions standing in
// for Python's MBA arithmetic obfuscation. Every training-condition structural
// feature is switched OFF (controlFlowFlattening=false is S1; deadCodeInjection=
// false is S2) and globals are not renamed, so the entry function stays a callable
// top-level binding and the output differs from S1/S2 by construction.
//
// Protocol (batch CLI, one node process per batch — mirrors obf/js/driver.mjs):
//   stdin : { jobs: [ { program_id, code, entry_point, seed,
//                       min_encoded_strings, min_mba_sites } ] }
//   stdout: one JSON line per job
//           { program_id, ok, code, entry_point, n_encoded, n_number_sites,
//             reason, error }
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const _jsDir = process.env.OBTUNE_JS_DIR
  ? new URL('file://' + process.env.OBTUNE_JS_DIR.replace(/\/?$/, '/'))
  : new URL('../../../../js/', import.meta.url);
const _require = createRequire(new URL('package.json', _jsDir));
const JsObf = _require('javascript-obfuscator');
const parser = _require('@babel/parser');
const _traverse = _require('@babel/traverse');
const traverse = _traverse.default || _traverse;

// Marker proving the rc4 stringArray actually fired (js-obfuscator names its array
// accessor `_0x<hex>`). If encoding degenerated to nothing, this is absent.
const STRINGARRAY_MARKER = /_0x[0-9a-f]{4,}/;

function countLiterals(code) {
  // Count source string/number literals to enforce the min quality bar (a variant
  // with no strings would make H1 spuriously easy — nothing gets encoded).
  let nStrings = 0;
  let nNumbers = 0;
  let ast;
  try {
    ast = parser.parse(code, { sourceType: 'script', allowReturnOutsideFunction: true });
  } catch (e) {
    try {
      ast = parser.parse(code, { sourceType: 'module', allowReturnOutsideFunction: true });
    } catch (e2) {
      return { nStrings: 0, nNumbers: 0, parseOk: false };
    }
  }
  traverse(ast, {
    StringLiteral() { nStrings++; },
    TemplateLiteral(path) { nStrings += path.node.quasis.length; },
    NumericLiteral() { nNumbers++; },
  });
  return { nStrings, nNumbers, parseOk: true };
}

const OBF_OPTIONS = {
  // The held-out feature set, and nothing else.
  stringArray: true,
  stringArrayEncoding: ['rc4'],
  stringArrayThreshold: 1,
  splitStrings: true,
  splitStringsChunkLength: 4,
  numbersToExpressions: true,
  // Every trainable-condition feature OFF.
  controlFlowFlattening: false,
  deadCodeInjection: false,
  renameGlobals: false, // keep the entry function callable as a global
  renameProperties: false,
  // Keep it inert / deterministic.
  selfDefending: false,
  debugProtection: false,
  compact: true,
};

function emit(rec) {
  process.stdout.write(JSON.stringify(rec) + '\n');
}

let job;
try {
  job = JSON.parse(readFileSync(0, 'utf8'));
} catch (e) {
  process.stderr.write('js_h1.mjs: bad stdin JSON: ' + (e && e.message) + '\n');
  process.exit(1);
}

const jobs = (job && Array.isArray(job.jobs)) ? job.jobs : [];
for (const j of jobs) {
  const base = { program_id: j.program_id, entry_point: j.entry_point };
  const minStrings = Number.isFinite(j.min_encoded_strings) ? j.min_encoded_strings : 1;
  try {
    const { nStrings, nNumbers, parseOk } = countLiterals(j.code);
    if (!parseOk) {
      emit({ ...base, ok: false, code: j.code, n_encoded: 0, n_number_sites: 0,
             reason: 'parse-error', error: null });
      continue;
    }
    if (nStrings < minStrings) {
      emit({ ...base, ok: false, code: j.code, n_encoded: nStrings, n_number_sites: nNumbers,
             reason: `too-few-strings: ${nStrings} < ${minStrings}`, error: null });
      continue;
    }
    const out = JsObf.obfuscate(j.code, { ...OBF_OPTIONS, seed: (j.seed | 0) || 1 }).getObfuscatedCode();
    if (!STRINGARRAY_MARKER.test(out) || out.trim() === j.code.trim()) {
      emit({ ...base, ok: false, code: out, n_encoded: nStrings, n_number_sites: nNumbers,
             reason: 'string-array-did-not-fire', error: null });
      continue;
    }
    emit({ ...base, ok: true, code: out, entry_point: j.entry_point,
           n_encoded: nStrings, n_number_sites: nNumbers, reason: null, error: null });
  } catch (e) {
    emit({ ...base, ok: false, code: j.code, n_encoded: 0, n_number_sites: 0,
           reason: null, error: String((e && e.stack) || e).slice(0, 2000) });
  }
}
