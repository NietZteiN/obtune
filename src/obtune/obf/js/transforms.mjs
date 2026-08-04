// Babel-based obfuscation transforms for the trainable JavaScript conditions.
//
// WHY Babel (not javascript-obfuscator): javascript-obfuscator's stringArray is
// default-on and its passes are entangled, so it would leak H1-family features
// (string encoding, `_0x` arrays) into whatever condition we asked for. The
// condition ladder demands SINGLE-TRANSFORM outputs with identical semantics to
// the L0 parent, so each condition here is a surgical AST rewrite over
// @babel/parser + @babel/traverse + @babel/generator, using authoritative scope
// info (scope.rename) rather than text substitution.
//
// Every condition strips comments (canon: comments/docstrings gone in ALL
// conditions). Determinism is a seeded mulberry32 passed from the Python side —
// never Math.random — so a (program, condition, seed) triple is reproducible.
//
// The transforms only ever touch bindings/structure they can prove are safe:
//   * renames go through scope.rename (real binding graph), never a regex;
//   * new identifiers avoid reserved words AND the program's free globals, so a
//     rename can never capture a global the code relies on (e.g. `Math`);
//   * S1 flattening keeps nested constructs intact and hoists top-level lexical
//     declarations to function scope, because the dispatch `while` re-enters the
//     `switch` block on every step and would otherwise re-create `let`/`const`
//     bindings each iteration (a subtle correctness trap — see hoisting below).
import { createRequire } from 'node:module';

// Resolve Babel from the committed js/ workspace. import.meta.url points at
// src/obtune/obf/js/transforms.mjs; four levels up is the project root, whose
// js/ holds node_modules. An env override keeps this robust if the tree moves.
const _jsDir = process.env.OBTUNE_JS_DIR
  ? new URL('file://' + process.env.OBTUNE_JS_DIR.replace(/\/?$/, '/'))
  : new URL('../../../../js/', import.meta.url);
const _require = createRequire(new URL('package.json', _jsDir));
const parser = _require('@babel/parser');
const _traverse = _require('@babel/traverse');
const _generate = _require('@babel/generator');
const t = _require('@babel/types');
// @babel/traverse and @babel/generator are CJS with an interop default under ESM.
const traverse = _traverse.default || _traverse;
const generate = _generate.default || _generate;

import { emit } from './emit.mjs';

// ---------------------------------------------------------------------------
// Seeded RNG (mulberry32) — small, fast, deterministic. Seeded from a 32-bit int.
// ---------------------------------------------------------------------------
function mulberry32(seed) {
  let a = seed >>> 0;
  return function rng() {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

function randInt(rng, lo, hi) {
  // inclusive range
  return lo + Math.floor(rng() * (hi - lo + 1));
}

function shuffle(arr, rng) {
  // Fisher-Yates with the seeded RNG (never Math.random).
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function distinctInts(rng, n, lo, hi) {
  const s = new Set();
  let guard = 0;
  while (s.size < n && guard++ < n * 50) s.add(randInt(rng, lo, hi));
  // Fallback (tiny range): top up sequentially past hi so ids stay distinct.
  let extra = hi + 1;
  while (s.size < n) s.add(extra++);
  return [...s];
}

// ---------------------------------------------------------------------------
// Identifier vocabularies and reserved-word guard.
// ---------------------------------------------------------------------------
const RESERVED = new Set([
  'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
  'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
  'if', 'import', 'in', 'instanceof', 'new', 'return', 'super', 'switch', 'this',
  'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'let',
  'static', 'enum', 'await', 'async', 'implements', 'package', 'protected',
  'interface', 'private', 'public', 'null', 'true', 'false', 'arguments', 'eval',
]);

const IDENT_RE = /^[A-Za-z_$][A-Za-z0-9_$]*$/;
const isValidIdent = (s) => IDENT_RE.test(s) && !RESERVED.has(s);

// L1b: entry function gets a plausible-but-unrelated domain name (the fibfib ->
// smoothArea trap). None of these contain an H1 marker substring.
const TRAP = [
  'smoothArea', 'parseToken', 'mergeBuffer', 'normalizeVector', 'computeMedian',
  'flushCache', 'resolvePath', 'encodeFrame', 'buildIndex', 'scaleMatrix',
  'hashRecord', 'splitRange', 'filterNodes', 'wrapHandler', 'projectPoint',
  'sampleGrid', 'alignRows', 'trackState', 'renderScene', 'foldRegion',
];
// L1b: other bindings get misleading domain nouns/verbs.
const MISLEAD = [
  'ctx', 'acc', 'tmp', 'node', 'slot', 'edge', 'span', 'bucket', 'cursor',
  'frame', 'token', 'chunk', 'region', 'vertex', 'stride', 'offset', 'handle',
  'record', 'window', 'segment', 'anchor', 'marker', 'weight', 'factor',
];
// Semantic-inversion table: a name whose meaning is inverted misleads a reader
// far more than a random string. Keys are matched as substrings (lowercased).
const INVERSIONS = [
  ['maximum', 'minimum'], ['minimum', 'maximum'], ['max', 'min'], ['min', 'max'],
  ['first', 'last'], ['last', 'first'], ['left', 'right'], ['right', 'left'],
  ['prime', 'composite'], ['sort', 'shuffle'], ['count', 'ignore'],
  ['push', 'pop'], ['head', 'tail'], ['even', 'odd'], ['odd', 'even'],
  ['prev', 'next'], ['start', 'end'], ['total', 'partial'], ['sum', 'product'],
  ['valid', 'broken'], ['open', 'closed'],
];
function invert(name) {
  const lower = name.toLowerCase();
  for (const [k, v] of INVERSIONS) if (lower.includes(k)) return v;
  return null;
}

// Sequential (L2) base-26 column names: 0->a, 25->z, 26->aa, ...
function base26(n) {
  let s = '';
  n += 1;
  while (n > 0) {
    n -= 1;
    s = String.fromCharCode(97 + (n % 26)) + s;
    n = Math.floor(n / 26);
  }
  return s;
}

// ---------------------------------------------------------------------------
// Parse / generate helpers.
// ---------------------------------------------------------------------------
function parseCode(code) {
  // Corpus programs expose their entry point as a global (the vm executor fetches
  // it by name after running the code), which only works for scripts, so parse as
  // a script first to preserve sloppy-mode semantics; fall back to module.
  const opts = {
    allowReturnOutsideFunction: true,
    allowSuperOutsideMethod: true,
    allowUndeclaredExports: true,
    errorRecovery: false,
  };
  try {
    return parser.parse(code, { ...opts, sourceType: 'script' });
  } catch (e) {
    return parser.parse(code, { ...opts, sourceType: 'module' });
  }
}

function gen(ast) {
  // Shared with L0 normalization (obf/js/emit.mjs): comments stripped in ALL
  // conditions, 4-space indentation, no blank lines, one trailing newline. Printing
  // differently here than the normalizer would make every identifier variant differ
  // from its L0 parent in whitespace as well as identifiers.
  return emit(ast, generate, parseCode);
}

function programGlobals(ast) {
  let names = [];
  traverse(ast, {
    Program(path) {
      path.scope.crawl();
      names = Object.keys(path.scope.globals || {});
    },
  });
  return names;
}

function collectBindings(ast) {
  const out = [];
  const seen = new Set();
  traverse(ast, {
    Scopable(path) {
      const scope = path.scope;
      for (const name of Object.keys(scope.bindings)) {
        const binding = scope.bindings[name];
        if (seen.has(binding)) continue;
        seen.add(binding);
        const id = binding.identifier;
        const pos = id && typeof id.start === 'number' ? id.start : 0;
        out.push({ scope, name, binding, pos });
      }
    },
  });
  return out;
}

function isFunctionLike(binding) {
  const p = binding && binding.path;
  if (!p) return false;
  if (
    p.isFunctionDeclaration() || p.isFunctionExpression() ||
    p.isArrowFunctionExpression() || p.isClassDeclaration() || p.isClassExpression()
  ) return true;
  if (p.isVariableDeclarator() && p.node.init) {
    const it = p.node.init.type;
    return it === 'FunctionExpression' || it === 'ArrowFunctionExpression' || it === 'ClassExpression';
  }
  return false;
}

function findEntryFunctionPath(ast, entryPoint) {
  let found = null;
  traverse(ast, {
    FunctionDeclaration(path) {
      if (found) return;
      if (path.node.id && path.node.id.name === entryPoint && path.parentPath.isProgram()) {
        found = path;
      }
    },
    VariableDeclarator(path) {
      if (found) return;
      const decl = path.parentPath;
      if (!decl.parentPath || !decl.parentPath.isProgram()) return;
      if (!t.isIdentifier(path.node.id, { name: entryPoint })) return;
      const init = path.node.init;
      if (init && (t.isFunctionExpression(init) || t.isArrowFunctionExpression(init))) {
        found = path.get('init');
      }
    },
  });
  return found;
}

// ---------------------------------------------------------------------------
// Renaming (L1r / L2 / L1b) — two-pass through unique temporaries so a final
// name can never capture a not-yet-renamed original binding.
// ---------------------------------------------------------------------------
/** Dotted path naming a scope, for disambiguating shadowed bindings in rename_map.
 *  Anonymous function scopes are labelled by their kind plus source position so the
 *  path stays stable across runs (positions come from the parse, not the RNG). */
function scopePath(scope) {
  const parts = [];
  for (let s = scope; s; s = s.parent) {
    const block = s.block;
    if (!block) continue;
    if (block.type === 'Program') {
      parts.push('top');
    } else if (block.id && block.id.name) {
      parts.push(block.id.name);
    } else {
      const pos = block.start ?? 0;
      parts.push(`${block.type}@${pos}`);
    }
  }
  return parts.reverse().join('.');
}

function renameAll(ast, entryPoint, factory) {
  const binds = collectBindings(ast);
  // Deterministic order: source position, then name. Drives L2's a,b,c sequence
  // and makes every condition reproducible from the seed.
  binds.sort((a, b) => a.pos - b.pos || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));

  // Pass 1: every binding -> a unique temporary. After this no original name
  // survives, so pass-2 targets cannot alias a live original binding.
  binds.forEach((b, i) => {
    const tmp = `_obt_${i}_`;
    b.scope.rename(b.name, tmp);
    b.tmp = tmp;
  });

  // Free globals and reserved words are off-limits for new names, otherwise a
  // rename could shadow (capture) a global the program depends on.
  const forbidden = new Set([...RESERVED, ...programGlobals(ast)]);
  const used = new Set();
  const renameMap = {};
  let newEntry = entryPoint;

  binds.forEach((b) => {
    let name;
    let attempt = 0;
    do {
      name = factory.next(b, attempt++);
    } while (!isValidIdent(name) || forbidden.has(name) || used.has(name));
    used.add(name);
    b.scope.rename(b.tmp, name);
    // rename_map must be LOSSLESS: the same source name can bind in several scopes
    // (two callbacks each taking `x`) and each gets a different new name. A flat
    // orig->new map would silently keep only the last, which breaks L1b decoy->true
    // recovery in the RQ3 analysis. Convention matches obf/py/rename.py: the first
    // binding of a name is stored bare, later ones are qualified with their scope path.
    const key = b.name in renameMap ? `${b.name}@${scopePath(b.scope)}` : b.name;
    renameMap[key] = name;
    const isEntry = b.name === entryPoint && b.scope.block && b.scope.block.type === 'Program';
    if (isEntry) newEntry = name;
  });

  return { renameMap, newEntry };
}

function seqFactory() {
  let c = 0;
  return { next() { return base26(c++); } };
}

function hexFactory(rng) {
  return {
    next(b) {
      const h = (randInt(rng, 0, 0xffff) & 0xffff).toString(16).padStart(4, '0');
      return (isFunctionLike(b) ? 'f_' : 'v_') + h;
    },
  };
}

function adversarialFactory(rng, entryPoint) {
  const pool = shuffle(MISLEAD, rng);
  const traps = shuffle(TRAP, rng);
  let poolIdx = 0;
  let trapIdx = 0;
  return {
    next(b, attempt) {
      const isEntry = b.scope.block && b.scope.block.type === 'Program' && b.name === entryPoint;
      let base;
      if (isEntry) {
        base = traps[trapIdx % traps.length];
        trapIdx++;
      } else {
        const inv = invert(b.name);
        if (inv && attempt === 0) {
          base = inv;
        } else {
          base = pool[poolIdx % pool.length];
          poolIdx++;
        }
      }
      if (attempt > 0) base = base + base26(attempt - 1);
      return base;
    },
  };
}

// ---------------------------------------------------------------------------
// Condition implementations.
// ---------------------------------------------------------------------------
function transformL0(code) {
  const ast = parseCode(code);
  return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: [] };
}

function transformRename(code, entryPoint, factory) {
  const ast = parseCode(code);
  const { renameMap, newEntry } = renameAll(ast, entryPoint, factory);
  return { ok: true, code: gen(ast), entryPoint: newEntry, renameMap, skippedConstructs: [] };
}

// L2 also strips type annotations. The trainable JS corpus is plain JS (parsed as
// script, so no TS/Flow nodes exist), which makes annotation stripping a no-op
// here — sequential minification is L2's operative transform for JS. We still run
// the strip so the contract holds if TS/Flow nodes are ever present.
function stripAnnotations(ast) {
  traverse(ast, {
    enter(path) {
      const n = path.node;
      if (n.typeAnnotation) n.typeAnnotation = null;
      if (n.returnType) n.returnType = null;
      if (n.typeParameters) n.typeParameters = null;
      if (
        t.isTSTypeAliasDeclaration && (t.isTSTypeAliasDeclaration(n) || t.isTSInterfaceDeclaration(n) ||
          t.isTSDeclareFunction(n) || t.isTSTypeAnnotation(n))
      ) {
        path.remove();
      }
    },
  });
}

function transformL2(code, entryPoint) {
  const ast = parseCode(code);
  stripAnnotations(ast);
  const { renameMap, newEntry } = renameAll(ast, entryPoint, seqFactory());
  return { ok: true, code: gen(ast), entryPoint: newEntry, renameMap, skippedConstructs: [] };
}

// --- S1: control-flow flattening -------------------------------------------
// Approach: turn the entry function's TOP-LEVEL statement sequence into a
// dispatch loop `while(true) switch(state)`. Nested constructs (if/for/while,
// nested functions) are left intact inside their state, so the transform is
// semantics-preserving for arbitrary nesting. The one correctness trap is
// lexical scope: the switch block is re-entered every loop step, so a `let`/
// `const` declared in one case would be a *fresh* binding on the next step. We
// therefore hoist every top-level binding to function scope (`var`), converting
// declarations to assignments that run in their state slot.
const S1_BAIL = {
  try: 'try',
  forAwait: 'for-await',
  generator: 'generator',
  label: 'labeled-break-continue',
  destructureLoop: 'destructuring-in-loop-head',
};

function s1BailScan(fnPath) {
  const skipped = new Set();
  if (fnPath.node.generator) skipped.add(S1_BAIL.generator);
  fnPath.traverse({
    TryStatement() { skipped.add(S1_BAIL.try); },
    Function(path) { if (path.node.generator) skipped.add(S1_BAIL.generator); },
    LabeledStatement() { skipped.add(S1_BAIL.label); },
    BreakStatement(path) { if (path.node.label) skipped.add(S1_BAIL.label); },
    ContinueStatement(path) { if (path.node.label) skipped.add(S1_BAIL.label); },
    ForOfStatement(path) {
      if (path.node.await) skipped.add(S1_BAIL.forAwait);
      if (t.isVariableDeclaration(path.node.left) &&
          path.node.left.declarations.some((d) => !t.isIdentifier(d.id))) {
        skipped.add(S1_BAIL.destructureLoop);
      }
    },
    ForInStatement(path) {
      if (t.isVariableDeclaration(path.node.left) &&
          path.node.left.declarations.some((d) => !t.isIdentifier(d.id))) {
        skipped.add(S1_BAIL.destructureLoop);
      }
    },
    ForStatement(path) {
      const init = path.node.init;
      if (t.isVariableDeclaration(init) &&
          init.declarations.some((d) => !t.isIdentifier(d.id))) {
        skipped.add(S1_BAIL.destructureLoop);
      }
    },
  });
  return [...skipped];
}

function collectPatternNames(node, out) {
  if (!node) return;
  if (t.isIdentifier(node)) out.add(node.name);
  else if (t.isAssignmentPattern(node)) collectPatternNames(node.left, out);
  else if (t.isRestElement(node)) collectPatternNames(node.argument, out);
  else if (t.isArrayPattern(node)) node.elements.forEach((e) => collectPatternNames(e, out));
  else if (t.isObjectPattern(node)) {
    node.properties.forEach((p) => {
      if (t.isRestElement(p)) collectPatternNames(p.argument, out);
      else collectPatternNames(p.value, out);
    });
  }
}

function s1ProcessStatement(stmt, hoistNames) {
  // Returns { hoist: node|null (moved before the loop), slot: [stmts for the state] }
  if (t.isFunctionDeclaration(stmt)) {
    return { hoist: stmt, slot: [] }; // hoisted anyway; move it out verbatim
  }
  if (t.isClassDeclaration(stmt) && stmt.id) {
    hoistNames.add(stmt.id.name);
    const ce = t.classExpression(stmt.id, stmt.superClass, stmt.body, stmt.decorators || []);
    return { hoist: null, slot: [t.expressionStatement(t.assignmentExpression('=', t.identifier(stmt.id.name), ce))] };
  }
  if (t.isVariableDeclaration(stmt)) {
    const assigns = [];
    for (const d of stmt.declarations) {
      collectPatternNames(d.id, hoistNames);
      if (d.init) assigns.push(t.expressionStatement(t.assignmentExpression('=', d.id, d.init)));
    }
    return { hoist: null, slot: assigns };
  }
  return { hoist: null, slot: [stmt] };
}

function transformS1(code, entryPoint, rng) {
  const ast = parseCode(code);
  const fnPath = findEntryFunctionPath(ast, entryPoint);
  if (!fnPath) {
    return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: ['entry-not-function'] };
  }
  const skipped = s1BailScan(fnPath);
  if (skipped.length) {
    // Leave verbatim (still comment-stripped/normalized) and report why.
    return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: skipped };
  }
  const fnNode = fnPath.node;

  // Arrow with an expression body: give it a block so it has a statement list.
  if (t.isArrowFunctionExpression(fnNode) && !t.isBlockStatement(fnNode.body)) {
    fnNode.body = t.blockStatement([t.returnStatement(fnNode.body)]);
  }
  const originalBody = fnNode.body.body;

  const hoistNames = new Set();
  const hoistDecls = [];
  const stateBodies = [];
  for (const stmt of originalBody) {
    const r = s1ProcessStatement(stmt, hoistNames);
    if (r.hoist) hoistDecls.push(r.hoist);
    if (r.slot.length) stateBodies.push(r.slot);
  }
  if (stateBodies.length === 0) {
    return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: ['no-flattenable-body'] };
  }

  // State ids: randomized, non-sequential, distinct. min_states = 3 (config); pad
  // with never-reached filler cases when the real body has fewer states.
  const MIN_STATES = 3;
  const total = Math.max(stateBodies.length, MIN_STATES);
  const ids = distinctInts(rng, total, 1000, 999999);
  const realIds = ids.slice(0, stateBodies.length);
  const fillerIds = ids.slice(stateBodies.length);

  const stateVar = '__s' + (randInt(rng, 0, 0xffff) & 0xffff).toString(16).padStart(4, '0');

  const cases = [];
  stateBodies.forEach((body, i) => {
    const stmts = body.slice();
    if (i < stateBodies.length - 1) {
      stmts.push(t.expressionStatement(t.assignmentExpression('=', t.identifier(stateVar), t.numericLiteral(realIds[i + 1]))));
      stmts.push(t.breakStatement());
    } else {
      // Falling off the end of the original body === returning undefined.
      stmts.push(t.returnStatement());
    }
    cases.push(t.switchCase(t.numericLiteral(realIds[i]), stmts));
  });
  // Filler (dead) cases: never entered, just point back at a real id.
  fillerIds.forEach((fid) => {
    const target = realIds[randInt(rng, 0, realIds.length - 1)];
    cases.push(t.switchCase(t.numericLiteral(fid), [
      t.expressionStatement(t.assignmentExpression('=', t.identifier(stateVar), t.numericLiteral(target))),
      t.breakStatement(),
    ]));
  });

  const shuffledCases = shuffle(cases, rng);
  shuffledCases.push(t.switchCase(null, [t.returnStatement()])); // default: guaranteed exit

  const dispatch = t.whileStatement(
    t.booleanLiteral(true),
    t.blockStatement([t.switchStatement(t.identifier(stateVar), shuffledCases)]),
  );

  const newBody = [...hoistDecls];
  if (hoistNames.size) {
    newBody.push(t.variableDeclaration('var', [...hoistNames].map((n) => t.variableDeclarator(t.identifier(n)))));
  }
  newBody.push(t.variableDeclaration('let', [t.variableDeclarator(t.identifier(stateVar), t.numericLiteral(realIds[0]))]));
  newBody.push(dispatch);
  fnNode.body.body = newBody;

  return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: [] };
}

// --- S2: opaque predicates + dead code --------------------------------------
// Opaque predicates are algebraic invariants on random integer literals:
//   n*n % 4 is always 0 or 1 for any integer n (JS % of a non-negative square is
//   non-negative), so `n*n % 4 === 3` is a constant FALSE and `!== 3` a constant
//   TRUE that a reader cannot fold at a glance. Both guard only dead branches, so
//   semantics are preserved. Dead helpers are never referenced.
function hexTag(rng) {
  return (randInt(rng, 0, 0xffff) & 0xffff).toString(16).padStart(4, '0');
}

function opaqueFalse(rng) {
  const n = randInt(rng, 2, 9999);
  return t.binaryExpression('===',
    t.binaryExpression('%', t.binaryExpression('*', t.numericLiteral(n), t.numericLiteral(n)), t.numericLiteral(4)),
    t.numericLiteral(3));
}
function opaqueTrue(rng) {
  const n = randInt(rng, 2, 9999);
  return t.binaryExpression('!==',
    t.binaryExpression('%', t.binaryExpression('*', t.numericLiteral(n), t.numericLiteral(n)), t.numericLiteral(4)),
    t.numericLiteral(3));
}

function deadBlock(rng) {
  // Never executed; a hoisted-but-unassigned var keeps it inert and marker-free.
  const v = '_z' + hexTag(rng);
  return t.blockStatement([
    t.variableDeclaration('var', [t.variableDeclarator(t.identifier(v),
      t.binaryExpression('*', t.numericLiteral(randInt(rng, 2, 99)), t.numericLiteral(randInt(rng, 2, 99))))]),
    t.returnStatement(t.identifier(v)),
  ]);
}

function opaqueGuard(rng) {
  if (rng() < 0.5) {
    return t.ifStatement(opaqueFalse(rng), deadBlock(rng));
  }
  return t.ifStatement(opaqueTrue(rng), t.blockStatement([]), deadBlock(rng));
}

function deadHelper(rng) {
  const name = '_dead' + hexTag(rng);
  const p = 'p' + hexTag(rng);
  const r = 'r' + hexTag(rng);
  const body = t.blockStatement([
    t.variableDeclaration('var', [t.variableDeclarator(t.identifier(r),
      t.binaryExpression('*', t.identifier(p), t.numericLiteral(randInt(rng, 2, 99))))]),
    t.returnStatement(t.binaryExpression('+', t.identifier(r), t.numericLiteral(randInt(rng, 1, 99)))),
  ]);
  return t.functionDeclaration(t.identifier(name), [t.identifier(p)], body);
}

function transformS2(code, entryPoint, rng) {
  const ast = parseCode(code);
  const fnPath = findEntryFunctionPath(ast, entryPoint);

  const nPred = randInt(rng, 1, 3);
  const nDead = randInt(rng, 1, 2);

  if (fnPath) {
    const fnNode = fnPath.node;
    if (t.isArrowFunctionExpression(fnNode) && !t.isBlockStatement(fnNode.body)) {
      fnNode.body = t.blockStatement([t.returnStatement(fnNode.body)]);
    }
    const body = fnNode.body.body;
    for (let i = 0; i < nPred; i++) {
      // Force the first guard to index 0 so at least one opaque predicate is on a
      // reachable path (a later splice could land after an early `return`).
      const at = i === 0 ? 0 : randInt(rng, 0, body.length);
      body.splice(at, 0, opaqueGuard(rng));
    }
  }

  // Dead helpers at program scope, never called.
  let programBody = null;
  traverse(ast, { Program(path) { programBody = path.node.body; } });
  for (let i = 0; i < nDead; i++) programBody.push(deadHelper(rng));

  return { ok: true, code: gen(ast), renameMap: {}, skippedConstructs: [] };
}

// ---------------------------------------------------------------------------
// Public dispatch.
// ---------------------------------------------------------------------------
export function applyTransform(condition, code, entryPoint, seed) {
  const rng = mulberry32((seed >>> 0) || 1);
  switch (condition) {
    case 'L0':
      return { entryPoint, ...transformL0(code) };
    case 'L1r':
      return transformRename(code, entryPoint, hexFactory(rng));
    case 'L2':
      return transformL2(code, entryPoint);
    case 'L1b':
      return transformRename(code, entryPoint, adversarialFactory(rng, entryPoint));
    case 'S1':
      return { entryPoint, ...transformS1(code, entryPoint, rng) };
    case 'S2':
      return { entryPoint, ...transformS2(code, entryPoint, rng) };
    default:
      throw new Error(`unknown or non-JS-trainable condition: ${condition}`);
  }
}
