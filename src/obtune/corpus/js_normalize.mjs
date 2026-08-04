// JavaScript-side helper for corpus/normalize.py. Babel only — javascript-obfuscator
// is reserved for the quarantined H1 generator (its default-on stringArray would leak
// H1 features into every condition that touched it).
//
// Protocol: one JSON job on stdin, one JSON object on stdout.
//   {op:"normalize", code}  -> {ok, code, protected_lines}
//   {op:"call",      code}  -> {ok, callee, args}          // split a call expression
//   {op:"names",     code}  -> {ok, names}                 // top-level binding names
//
// Why re-indent here rather than in Python: @babel/generator dropped its `indent`
// option in v7, so the 2-space output has to be widened afterwards — and that is only
// safe with the AST in hand, since leading whitespace inside a multi-line template
// literal is part of the string value, not indentation.

import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// The canonical emission settings, shared with every obfuscation condition.
import { GENERATE_OPTS } from '../obf/js/emit.mjs';

// Babel lives in <project>/js/node_modules, not next to this file, and ESM resolution
// is anchored at the importing file rather than the CWD. createRequire re-anchors
// resolution at the js workspace so this helper can stay in src/obtune/corpus/.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const JS_ROOT = process.env.OBTUNE_JS_ROOT || path.resolve(HERE, '..', '..', '..', '..', 'js');
const req = createRequire(path.join(JS_ROOT, 'package.json'));

const { parse } = req('@babel/parser');
const generatorPkg = req('@babel/generator');
const generate = generatorPkg.default ?? generatorPkg;

const PARSE_OPTS = {
  sourceType: 'unambiguous',
  errorRecovery: false,
  allowReturnOutsideFunction: true,
  plugins: ['classProperties', 'objectRestSpread', 'optionalChaining', 'nullishCoalescingOperator'],
};

function read() {
  const chunks = [];
  return new Promise((resolve, reject) => {
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => chunks.push(c));
    process.stdin.on('end', () => resolve(chunks.join('')));
    process.stdin.on('error', reject);
  });
}

/** 1-based physical line numbers that lie strictly inside a multi-line string value.
 *  Their leading/trailing whitespace is data and must survive normalization. */
function protectedLines(code) {
  const ast = parse(code, PARSE_OPTS);
  const lines = new Set();
  const walk = (node) => {
    if (node === null || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    if (typeof node.type === 'string' && node.loc &&
        (node.type === 'TemplateElement' || node.type === 'StringLiteral')) {
      for (let l = node.loc.start.line + 1; l <= node.loc.end.line; l++) lines.add(l);
    }
    for (const k of Object.keys(node)) {
      if (k === 'loc' || k === 'leadingComments' || k === 'trailingComments') continue;
      walk(node[k]);
    }
  };
  walk(ast.program);
  return lines;
}

/** Widen Babel's 2-space indentation to 4, skipping protected lines. Babel always
 *  emits exactly two spaces per nesting level and never tabs, so doubling the leading
 *  run of spaces is an exact level-preserving transform. */
function widenIndent(code, protectedSet) {
  return code
    .split('\n')
    .map((line, i) => {
      if (protectedSet.has(i + 1)) return line;
      const m = /^( *)(.*)$/.exec(line);
      return ' '.repeat(m[1].length * 2) + m[2].replace(/\s+$/, '');
    })
    .join('\n');
}

function opNormalize(code) {
  const ast = parse(code, PARSE_OPTS);
  // Printing goes through the SHARED emitter (obf/js/emit.mjs) that every other JS
  // condition uses. Keeping a second copy of this logic here is how L0 and L1r came
  // to disagree on indentation, which made every identifier variant differ from its
  // parent in whitespace as well as identifiers.
  const out = { code: generate(ast, GENERATE_OPTS).code };
  const prot = protectedLines(out.code);
  const widened = widenIndent(out.code, prot);
  // Re-derive protection against the widened text: line numbers are unchanged by
  // widening (it never adds or removes lines), so the same set applies.
  const kept = [];
  const keptProtected = [];
  widened.split('\n').forEach((line, i) => {
    const isProt = prot.has(i + 1);
    if (isProt || line.trim() !== '') {
      kept.push(line);
      if (isProt) keptProtected.push(kept.length);
    }
  });
  return { ok: true, code: kept.join('\n') + (kept.length ? '\n' : ''), protected_lines: keptProtected };
}

function opCall(code) {
  const ast = parse(code, PARSE_OPTS);
  const stmt = ast.program.body[0];
  const expr = stmt && stmt.type === 'ExpressionStatement' ? stmt.expression : null;
  if (!expr || expr.type !== 'CallExpression') throw new Error('not a call expression');
  const callee = expr.callee.type === 'Identifier' ? expr.callee.name : null;
  const args = expr.arguments.map((a) => generate(a, { comments: false, concise: true }).code);
  return { ok: true, callee, args };
}

function opNames(code) {
  const ast = parse(code, PARSE_OPTS);
  const names = [];
  const push = (n) => { if (n && !names.includes(n)) names.push(n); };
  const fromPattern = (p) => {
    if (!p) return;
    if (p.type === 'Identifier') push(p.name);
    else if (p.type === 'ObjectPattern') p.properties.forEach((q) => fromPattern(q.value ?? q.argument));
    else if (p.type === 'ArrayPattern') p.elements.forEach(fromPattern);
    else if (p.type === 'AssignmentPattern') fromPattern(p.left);
    else if (p.type === 'RestElement') fromPattern(p.argument);
  };
  for (const node of ast.program.body) {
    if (node.type === 'FunctionDeclaration') push(node.id && node.id.name);
    else if (node.type === 'ClassDeclaration') push(node.id && node.id.name);
    else if (node.type === 'VariableDeclaration') node.declarations.forEach((d) => fromPattern(d.id));
    else if (node.type === 'ExportNamedDeclaration' && node.declaration) {
      if (node.declaration.type === 'FunctionDeclaration') push(node.declaration.id && node.declaration.id.name);
      else if (node.declaration.type === 'VariableDeclaration') {
        node.declaration.declarations.forEach((d) => fromPattern(d.id));
      }
    }
  }
  return { ok: true, names };
}

// Host/builtin names that must survive alpha-canonicalization: renaming them would
// make `Math.max(...)` and `foo.max(...)` hash alike, which is a false duplicate.
const JS_GLOBALS = new Set([
  'Math', 'JSON', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Map', 'Set',
  'RegExp', 'Error', 'TypeError', 'RangeError', 'BigInt', 'Symbol', 'Date', 'Promise',
  'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'console', 'undefined', 'NaN',
  'Infinity', 'encodeURIComponent', 'decodeURIComponent', 'Int32Array', 'Float64Array',
  'Uint8Array', 'ArrayBuffer', 'globalThis', 'arguments',
]);

/** Rename every non-global identifier to a0, a1, ... in first-appearance order and
 *  print compactly. This is corpus/dedup.py's JS fallback canonicalizer: it is
 *  scope-blind by design (two programs differing only in which scope a name lives in
 *  are the same program for dedup), and it leaves member-property and object-key names
 *  alone because those are API surface, not the program's own naming. */
function opAlpha(code) {
  const ast = parse(code, PARSE_OPTS);
  const map = new Map();
  const alias = (n) => {
    if (!map.has(n)) map.set(n, `a${map.size}`);
    return map.get(n);
  };
  const walk = (node, parent, key) => {
    if (node === null || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach((c) => walk(c, parent, key));
      return;
    }
    if (node.type === 'Identifier' && !JS_GLOBALS.has(node.name)) {
      const isProperty = parent && (
        (parent.type === 'MemberExpression' && key === 'property' && !parent.computed) ||
        (parent.type === 'ObjectProperty' && key === 'key' && !parent.computed) ||
        (parent.type === 'ObjectMethod' && key === 'key' && !parent.computed) ||
        (parent.type === 'ClassMethod' && key === 'key' && !parent.computed)
      );
      if (!isProperty) node.name = alias(node.name);
    }
    for (const k of Object.keys(node)) {
      if (k === 'loc' || k === 'start' || k === 'end' || k === 'range') continue;
      walk(node[k], node, k);
    }
  };
  walk(ast.program, null, null);
  const out = generate(ast, { comments: false, concise: true, compact: true });
  return { ok: true, code: out.code };
}

const OPS = { normalize: opNormalize, call: opCall, names: opNames, alpha: opAlpha };

read()
  .then((raw) => {
    const job = JSON.parse(raw);
    const fn = OPS[job.op];
    if (!fn) throw new Error(`unknown op: ${job.op}`);
    process.stdout.write(JSON.stringify(fn(job.code)));
  })
  .catch((e) => {
    process.stdout.write(JSON.stringify({ ok: false, error: String((e && e.message) || e) }));
    process.exitCode = 0;
  });
