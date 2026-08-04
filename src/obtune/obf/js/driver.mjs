// Batch CLI for the JavaScript transforms. One node process per BATCH — Node's
// ~89 ms startup is amortized over the whole batch instead of paid per program.
//
// Protocol (mirrors exec/runner_js.mjs): read one JSON job object on stdin,
//   { jobs: [ { program_id, condition, code, entry_point, seed }, ... ] }
// write ONE JSON result line per job to stdout,
//   { program_id, condition, ok, code, entry_point, rename_map,
//     skipped_constructs, error }
// A transform that throws yields ok:false with the original code/entry echoed
// back so the Python side always has a well-formed row.
import { readFileSync } from 'node:fs';
import { applyTransform } from './transforms.mjs';

function emit(rec) {
  process.stdout.write(JSON.stringify(rec) + '\n');
}

let job;
try {
  job = JSON.parse(readFileSync(0, 'utf8'));
} catch (e) {
  // Unparseable stdin is a harness bug, not a per-job failure: fail loudly.
  process.stderr.write('driver.mjs: bad stdin JSON: ' + (e && e.message) + '\n');
  process.exit(1);
}

const jobs = (job && Array.isArray(job.jobs)) ? job.jobs : [];
for (const j of jobs) {
  const base = {
    program_id: j.program_id,
    condition: j.condition,
    entry_point: j.entry_point,
    rename_map: {},
    skipped_constructs: [],
  };
  try {
    const r = applyTransform(j.condition, j.code, j.entry_point, (j.seed | 0));
    emit({
      ...base,
      ok: !!r.ok,
      code: r.code,
      entry_point: r.entryPoint ?? j.entry_point,
      rename_map: r.renameMap || {},
      skipped_constructs: r.skippedConstructs || [],
      error: null,
    });
  } catch (e) {
    emit({
      ...base,
      ok: false,
      code: j.code, // echo the input so downstream still has the source
      error: String((e && e.stack) || e).slice(0, 2000),
    });
  }
}
