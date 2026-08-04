// Child process for the JavaScript batch executor. Mirrors runner_py.py's protocol.
// Reads one JSON job on stdin, writes one JSON result line per case on stdout.
//
// Isolation: the program runs in a vm context with a frozen minimal global — no
// require, process, fetch, timers, or module loader. The parent enforces a
// wall-clock timeout and kills the process group.

import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { canon, Unserializable } from './canon.mjs';

const job = JSON.parse(readFileSync(0, 'utf8'));
const perCaseTimeoutMs = job.timeout_ms ?? 2000;

const sandbox = {
  Math, JSON, Object, Array, String, Number, Boolean, Date: undefined,
  Map, Set, RegExp, Error, TypeError, RangeError, BigInt, Symbol,
  parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent,
  Int32Array, Float64Array, Uint8Array, ArrayBuffer,
  console: { log() {}, error() {}, warn() {} },
};
const context = vm.createContext(sandbox, { codeGeneration: { strings: false, wasm: false } });

function emit(rec) {
  process.stdout.write(JSON.stringify(rec) + '\n');
}

let fn;
try {
  vm.runInContext(job.code, context, { timeout: perCaseTimeoutMs, filename: '<program>' });
  fn = vm.runInContext(job.entry_point, context, { timeout: perCaseTimeoutMs });
  if (typeof fn !== 'function') throw new TypeError(`entry point ${job.entry_point} is not a function`);
} catch (e) {
  for (let i = 0; i < job.cases.length; i++) {
    emit({ i, status: 'error', output: null, exc_type: e?.constructor?.name ?? 'Error', elapsed_ms: 0 });
  }
  process.exit(0);
}

for (let i = 0; i < job.cases.length; i++) {
  const t0 = process.hrtime.bigint();
  let rec;
  try {
    // args_repr is a JS literal argument tuple, e.g. "(3, [1, 2])". Evaluated inside
    // the sandbox so it cannot reach host globals.
    const args = vm.runInContext(`[${job.cases[i].args_repr.replace(/^\s*\(|\)\s*$/g, '')}]`, context,
      { timeout: perCaseTimeoutMs });
    const value = vm.runInContext('__obtune_fn.apply(null, __obtune_args)',
      Object.assign(context, { __obtune_fn: fn, __obtune_args: args }),
      { timeout: perCaseTimeoutMs });
    rec = { i, status: 'ok', output: canon(value), exc_type: null };
  } catch (e) {
    if (e instanceof Unserializable) {
      rec = { i, status: 'unserializable', output: null, exc_type: String(e.message).slice(0, 120) };
    } else if (e?.code === 'ERR_SCRIPT_EXECUTION_TIMEOUT' || e?.code === 'ERR_SCRIPT_EXECUTION_INTERRUPTED') {
      // The vm watchdog fired: this is a hung program, not an exception the program raised.
      rec = { i, status: 'timeout', output: null, exc_type: null };
    } else {
      // Exception TYPE only — renaming changes messages, so messages are not comparable.
      rec = { i, status: 'raised', output: null, exc_type: e?.constructor?.name ?? 'Error' };
    }
  }
  rec.elapsed_ms = Number(process.hrtime.bigint() - t0) / 1e6;
  emit(rec);
}
